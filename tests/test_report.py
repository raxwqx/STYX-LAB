import contextlib
import io
import json
import socket
import tempfile
import threading
import unittest
from http.client import HTTPException
from pathlib import Path
from unittest.mock import patch

from lab.report import assess, main as report_main, to_markdown, write_reports
from lab.web.security_headers_lab import SECURITY_HEADERS, create_server


def _unused_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def running_server(profile):
    server = create_server(profile, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


class OversizedResponse:
    status = 200
    headers = {}

    def read(self, size=-1):
        return b"x" * (size if size and size > 0 else 16)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class AssessmentReportTests(unittest.TestCase):
    def test_port_validation(self):
        for port in (0, -1, 65536, "8766", True):
            with self.subTest(port=port), self.assertRaises(ValueError):
                assess(port)

    def test_timeout_validation(self):
        for timeout in (0, -1, 31, "2", True):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                assess(8766, timeout=timeout)

    def test_unavailable_local_endpoint_is_reported_without_crashing(self):
        report = assess(_unused_port(), timeout=0.1)
        self.assertEqual(report["status"], "unavailable")
        self.assertEqual(report["checks"][0]["status"], "fail")
        self.assertIn("127.0.0.1", report["target"])
        self.assertEqual(report["findings"], [])

    def test_malformed_http_response_is_reported_as_unavailable(self):
        with patch("lab.report.urlopen", side_effect=HTTPException("bad status line")):
            report = assess(8766)
        self.assertEqual(report["status"], "unavailable")
        self.assertIn("Could not obtain", report["error"])

    def test_oversized_response_is_reported_as_unavailable(self):
        with patch("lab.report.urlopen", return_value=OversizedResponse()):
            report = assess(8766)
        self.assertEqual(report["status"], "unavailable")
        self.assertIn("size limit", report["error"])

    def test_live_secure_lab_assessment_passes(self):
        with running_server("secure") as port:
            report = assess(port, timeout=2)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["profile"], "secure")
        # README documents nine checks for a complete valid response.
        self.assertEqual(len(report["checks"]), 9)
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["finding_summary"]["total"], 0)

    def test_live_baseline_assessment_checks_absence(self):
        with running_server("baseline") as port:
            report = assess(port, timeout=2)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["profile"], "baseline")
        self.assertGreater(report["finding_summary"]["total"], 0)

    def test_live_weak_assessment_passes_but_reports_findings(self):
        with running_server("weak") as port:
            report = assess(port, timeout=2)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["profile"], "weak")
        identifiers = {finding["id"] for finding in report["findings"]}
        self.assertIn("csp-unsafe-inline", identifiers)
        self.assertIn("x-frame-options-value", identifiers)
        self.assertEqual(
            report["finding_summary"]["total"], len(report["findings"])
        )

    def test_markdown_report_has_summary_and_scope_note(self):
        report = {
            "status": "pass", "version": "1.1.0", "created_at": "test-time",
            "target": "http://127.0.0.1:8766", "profile": "secure",
            "scope": "loopback only", "checks": [
                {"id": "headers", "status": "pass", "detail": "All headers present"}
            ], "summary": {"total": 1, "passed": 1, "failed": 0},
        }
        markdown = to_markdown(report)
        self.assertIn("STYX-LAB Local Security Assessment", markdown)
        self.assertIn("All headers present", markdown)
        self.assertIn("not a full security audit", markdown)

    def test_markdown_report_lists_findings_and_remediation(self):
        report = {
            "status": "pass", "version": "1.1.0", "profile": "weak",
            "checks": [], "summary": {"total": 0, "passed": 0, "failed": 0},
            "findings": [{
                "id": "csp-wildcard", "severity": "HIGH",
                "header": "Content-Security-Policy",
                "message": "CSP allows every source (*)",
                "remediation": "Use explicit origins",
            }],
            "finding_summary": {
                "CRITICAL": 0, "HIGH": 1, "MEDIUM": 0, "LOW": 0, "INFO": 0,
                "total": 1,
            },
        }
        markdown = to_markdown(report)
        self.assertIn("Header Findings", markdown)
        self.assertIn("CSP allows every source", markdown)
        self.assertIn("Use explicit origins", markdown)
        self.assertIn("Header findings: 1", markdown)

    def test_report_cli_writes_passed_json_and_markdown(self):
        with running_server("secure") as port:
            with tempfile.TemporaryDirectory() as directory:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exit_code = report_main([
                        "--port", str(port),
                        "--output-dir", directory,
                    ])
                self.assertEqual(exit_code, 0, output.getvalue())
                json_path = Path(directory) / "latest-assessment.json"
                markdown_path = Path(directory) / "latest-assessment.md"
                self.assertTrue(json_path.is_file())
                self.assertTrue(markdown_path.is_file())
                payload = json.loads(json_path.read_text(encoding="utf-8"))
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["summary"]["failed"], 0)
                self.assertEqual(payload["findings"], [])
                self.assertIn("Result:", markdown_path.read_text(encoding="utf-8"))

    def test_fail_on_threshold_triggers_for_weak_profile(self):
        with running_server("weak") as port:
            with tempfile.TemporaryDirectory() as directory:
                errors = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()):
                    with contextlib.redirect_stderr(errors):
                        exit_code = report_main([
                            "--port", str(port),
                            "--output-dir", directory,
                            "--fail-on", "medium",
                        ])
                payload = json.loads(
                    (Path(directory) / "latest-assessment.json").read_text(encoding="utf-8")
                )
        self.assertEqual(exit_code, 1)
        self.assertTrue(payload["fail_on_triggered"])
        self.assertEqual(payload["fail_on"], "medium")
        self.assertIn("fail-on", errors.getvalue().lower())

    def test_fail_on_threshold_does_not_trigger_for_secure_profile(self):
        with running_server("secure") as port:
            with tempfile.TemporaryDirectory() as directory:
                with contextlib.redirect_stdout(io.StringIO()):
                    exit_code = report_main([
                        "--port", str(port),
                        "--output-dir", directory,
                        "--fail-on", "low",
                    ])
        self.assertEqual(exit_code, 0)

    def test_report_cli_reports_unwritable_output_directory(self):
        with tempfile.NamedTemporaryFile() as handle:
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                exit_code = report_main(["--port", str(_unused_port()), "--output-dir", handle.name])
            self.assertEqual(exit_code, 1)
            self.assertIn("could not write reports", output.getvalue())

    def test_writes_both_report_formats(self):
        report = {
            "status": "unavailable", "version": "1.1.0", "created_at": "test-time",
            "target": "http://127.0.0.1:8766", "scope": "loopback only",
            "checks": [{"id": "endpoint", "status": "fail", "detail": "Offline"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            json_path, md_path = write_reports(report, directory)
            self.assertTrue(json_path.is_file())
            self.assertTrue(md_path.is_file())
            self.assertIn('"status": "unavailable"', json_path.read_text(encoding="utf-8"))
            self.assertIn("STYX-LAB Local Security Assessment", md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
