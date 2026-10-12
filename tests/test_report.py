import contextlib
import io
import json
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from lab.report import assess, main as report_main, to_markdown, write_reports
from lab.web.security_headers_lab import SECURITY_HEADERS, create_server


class AssessmentReportTests(unittest.TestCase):
    def test_port_validation(self):
        for port in (0, -1, 65536, "8766", True):
            with self.subTest(port=port), self.assertRaises(ValueError):
                assess(port)

    def test_unavailable_local_endpoint_is_reported_without_crashing(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            unused_port = sock.getsockname()[1]
        report = assess(unused_port, timeout=0.1)
        self.assertEqual(report["status"], "unavailable")
        self.assertEqual(report["checks"][0]["status"], "fail")
        self.assertIn("127.0.0.1", report["target"])

    def test_live_secure_lab_assessment_passes(self):
        server = create_server("secure", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            report = assess(server.server_address[1], timeout=2)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["summary"]["failed"], 0)
            self.assertEqual(report["profile"], "secure")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_live_baseline_assessment_checks_absence(self):
        server = create_server("baseline", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            report = assess(server.server_address[1], timeout=2)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["summary"]["failed"], 0)
            self.assertEqual(report["profile"], "baseline")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_markdown_report_has_summary_and_scope_note(self):
        report = {
            "status": "pass", "version": "1.0.1", "created_at": "test-time",
            "target": "http://127.0.0.1:8766", "profile": "secure",
            "scope": "loopback only", "checks": [
                {"id": "headers", "status": "pass", "detail": "All headers present"}
            ], "summary": {"total": 1, "passed": 1, "failed": 0},
        }
        markdown = to_markdown(report)
        self.assertIn("STYX-LAB Local Security Assessment", markdown)
        self.assertIn("All headers present", markdown)
        self.assertIn("not a full security audit", markdown)

    def test_report_cli_writes_passed_json_and_markdown(self):
        server = create_server("secure", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exit_code = report_main([
                        "--port", str(server.server_address[1]),
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
                self.assertIn("Result:", markdown_path.read_text(encoding="utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_writes_both_report_formats(self):
        report = {
            "status": "unavailable", "version": "1.0.1", "created_at": "test-time",
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
