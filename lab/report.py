"""Generate evidence-based reports about a local STYX-LAB endpoint."""

import argparse
from datetime import datetime, timezone
from http.client import HTTPException
import json
from pathlib import Path
import sys
from urllib.request import urlopen

from lab.headers import analyze, meets_threshold, summarize
from lab.web.security_headers_lab import (
    HOST,
    PROFILE_HEADERS,
    PROFILES,
    SECURITY_HEADERS,
    VERSION,
)

MAX_RESPONSE_BYTES = 1_000_000
MAX_TIMEOUT = 30.0

INTERPRETATIONS = {
    "secure": (
        "PASS means this local lab matched the configured secure profile for the "
        "checks performed. It is not a full application security audit."
    ),
    "baseline": (
        "The baseline intentionally omits the training security headers. "
        "PASS means the teaching baseline behaved as documented; it does not mean "
        "a production deployment is secure."
    ),
    "weak": (
        "The weak profile intentionally sends unsafe header values. "
        "PASS means the lab matched its documented weak configuration, and the "
        "findings describe why that configuration must never reach production."
    ),
}


def _validate_timeout(timeout):
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("Timeout must be a number.")
    if not 0 < timeout <= MAX_TIMEOUT:
        raise ValueError(
            f"Timeout must be greater than 0 and at most {MAX_TIMEOUT:g} seconds."
        )


def _get_json(url, timeout=2):
    with urlopen(url, timeout=timeout) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("response body exceeds the size limit")
        return (
            response.status,
            json.loads(raw.decode("utf-8")),
            response.headers,
        )


def assess(port=8766, timeout=2):
    """Assess one explicitly selected loopback STYX-LAB port only."""
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("Port must be an integer from 1 to 65535.")
    _validate_timeout(timeout)
    base = f"http://{HOST}:{port}"
    report = {
        "schema_version": 2,
        "tool": "STYX-LAB",
        "version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target": base,
        "scope": "IPv4 loopback only; no external hosts contacted",
        "checks": [],
        "findings": [],
        "finding_summary": summarize([]),
    }

    try:
        status, metadata, headers = _get_json(base + "/api/headers", timeout)
        health_status, health, _ = _get_json(base + "/health", timeout)
    except (OSError, ValueError, HTTPException) as exc:
        # URLError/HTTPError are OSError; JSONDecodeError is ValueError;
        # malformed HTTP framing raises http.client.HTTPException.
        report["status"] = "unavailable"
        report["error"] = f"Could not obtain a valid local STYX-LAB response: {exc}"
        report["checks"].append({
            "id": "endpoint-reachable",
            "status": "fail",
            "detail": "Local endpoint did not return the expected response.",
        })
        return report

    if not isinstance(health, dict) or not isinstance(metadata, dict):
        report["status"] = "unavailable"
        report["error"] = "A local STYX-LAB endpoint returned JSON that was not an object."
        report["checks"].append({
            "id": "response-schema",
            "status": "fail",
            "detail": "The health and header metadata responses must be JSON objects.",
        })
        return report

    profile = health.get("profile")
    report["profile"] = profile
    report["checks"].append({
        "id": "endpoint-reachable",
        "status": "pass" if status == 200 and health_status == 200 else "fail",
        "detail": f"/api/headers HTTP {status}; /health HTTP {health_status}",
    })
    report["checks"].append({
        "id": "health-profile",
        "status": "pass" if health.get("status") == "ok" and profile in PROFILES else "fail",
        "detail": f"Health status={health.get('status')!r}; profile={profile!r}",
    })

    expected_headers = PROFILE_HEADERS.get(profile, {})
    metadata_profile_ok = metadata.get("profile") == profile
    report["checks"].append({
        "id": "header-metadata-profile",
        "status": "pass" if metadata_profile_ok else "fail",
        "detail": f"Metadata profile={metadata.get('profile')!r}; health profile={profile!r}",
    })
    metadata_headers_ok = metadata.get("headers") == expected_headers
    report["checks"].append({
        "id": "header-metadata-values",
        "status": "pass" if metadata_headers_ok else "fail",
        "detail": (
            "Header metadata matches the declared profile."
            if metadata_headers_ok
            else "Header metadata does not match the declared profile."
        ),
    })

    for name in SECURITY_HEADERS:
        expected = expected_headers.get(name)
        observed = headers.get(name)
        passed = observed == expected
        if expected is None:
            detail = f"Observed {observed!r}; expected header absent"
        else:
            detail = f"Observed {observed!r}; expected {expected!r}"
        report["checks"].append({
            "id": "header:" + name.lower(),
            "status": "pass" if passed else "fail",
            "detail": detail,
        })

    # Graded analysis of the values actually sent by the endpoint. This
    # complements the exact-match checks: a header may match the profile and
    # still be weak by design, which is exactly what the weak profile teaches.
    report["findings"] = analyze(headers)
    report["finding_summary"] = summarize(report["findings"])

    failures = sum(check["status"] != "pass" for check in report["checks"])
    report["summary"] = {
        "total": len(report["checks"]),
        "passed": len(report["checks"]) - failures,
        "failed": failures,
    }
    report["status"] = "pass" if failures == 0 else "fail"
    report["interpretation"] = INTERPRETATIONS.get(
        profile,
        "PASS means the listed checks matched the observed local configuration. "
        "It is not a full application security audit.",
    )
    return report


def to_markdown(report):
    lines = [
        "# STYX-LAB Local Security Assessment",
        "",
        f"- **Result:** `{report.get('status', 'unknown').upper()}`",
        f"- **Version:** `{report.get('version', VERSION)}`",
        f"- **Created (UTC):** `{report.get('created_at', 'unknown')}`",
        f"- **Target:** `{report.get('target', 'unknown')}`",
        f"- **Profile:** `{report.get('profile', 'unavailable')}`",
        f"- **Scope:** {report.get('scope', 'local only')}",
        f"- **Interpretation:** {report.get('interpretation', 'This report covers only the listed checks.')}",
        "",
        "## Checks",
        "",
        "| Check | Result | Evidence |",
        "|---|---|---|",
    ]
    for check in report.get("checks", []):
        detail = str(check.get("detail", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{check.get('id', 'unknown')}` | **{check.get('status', 'unknown').upper()}** | {detail} |")

    findings = report.get("findings") or []
    lines.extend(["", "## Header Findings", ""])
    if findings:
        lines.extend([
            "| Severity | Header | Finding | Remediation |",
            "|---|---|---|---|",
        ])
        for finding in findings:
            severity = str(finding.get("severity", "INFO")).upper()
            header = str(finding.get("header", "")).replace("|", "\\|").replace("\n", " ")
            message = str(finding.get("message", "")).replace("|", "\\|").replace("\n", " ")
            remediation = str(finding.get("remediation", "")).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| **{severity}** | {header} | {message} | {remediation} |")
    else:
        lines.append("No header quality findings were produced.")

    if report.get("summary"):
        summary = report["summary"]
        lines.extend([
            "",
            "## Summary",
            "",
            f"- Total checks: {summary['total']}",
            f"- Passed: {summary['passed']}",
            f"- Failed: {summary['failed']}",
        ])
    if report.get("finding_summary"):
        finding_summary = report["finding_summary"]
        lines.extend([
            f"- Header findings: {finding_summary.get('total', 0)}",
            "- By severity: "
            + ", ".join(
                f"{severity} {finding_summary.get(severity, 0)}"
                for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
            ),
        ])
    if report.get("fail_on"):
        lines.append(f"- Fail-on threshold: `{report['fail_on']}`")
    if report.get("error"):
        lines.extend(["", "## Error", "", report["error"]])
    lines.extend([
        "",
        "> This report is a local training check, not a full security audit.",
        "> Review the application, test environment, and policies before making deployment decisions.",
        "",
    ])
    return "\n".join(lines)


def write_reports(report, output_dir=Path("reports")):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "latest-assessment.json"
    md_path = output_dir / "latest-assessment.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(report), encoding="utf-8")
    return json_path, md_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Assess a local STYX-LAB instance and save JSON/Markdown evidence."
    )
    parser.add_argument("--port", type=int, default=8766, help="Loopback port to assess (default: 8766).")
    parser.add_argument("--output-dir", default="reports", help="Output folder (default: reports).")
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help=f"Per-request timeout in seconds, up to {MAX_TIMEOUT:g} (default: 2).",
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "low", "medium", "high", "critical"),
        default="none",
        help="Return status 1 when a finding meets this severity (default: none).",
    )
    args = parser.parse_args(argv)

    try:
        report = assess(args.port, timeout=args.timeout)
    except ValueError as exc:
        parser.error(str(exc))

    report["fail_on"] = args.fail_on
    report["fail_on_triggered"] = meets_threshold(report.get("findings", []), args.fail_on)

    try:
        json_path, md_path = write_reports(report, args.output_dir)
    except OSError as exc:
        print(f"error: could not write reports: {exc}", file=sys.stderr)
        return 1

    summary = report.get("finding_summary", {})
    print(f"Assessment result: {report['status'].upper()}")
    print(f"Header findings: {summary.get('total', 0)}")
    print(f"Fail-on: {args.fail_on}")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")

    if report.get("fail_on_triggered"):
        print(
            f"error: --fail-on {args.fail_on}: findings at or above "
            f"'{args.fail_on}' severity were detected",
            file=sys.stderr,
        )
    if report["status"] != "pass" or report.get("fail_on_triggered"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
