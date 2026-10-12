"""Generate evidence-based reports about a local STYX-LAB endpoint."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

from lab.web.security_headers_lab import HOST, SECURITY_HEADERS, VERSION


def _get_json(url, timeout=2):
    with urlopen(url, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8")), response.headers


def assess(port=8766, timeout=2):
    """Assess one explicitly selected loopback STYX-LAB port only."""
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("Port must be an integer from 1 to 65535.")
    base = f"http://{HOST}:{port}"
    report = {
        "schema_version": 1,
        "tool": "STYX-LAB",
        "version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target": base,
        "scope": "IPv4 loopback only; no external hosts contacted",
        "checks": [],
    }

    try:
        status, metadata, headers = _get_json(base + "/api/headers", timeout)
        health_status, health, _ = _get_json(base + "/health", timeout)
    except (OSError, URLError, HTTPError, ValueError, json.JSONDecodeError) as exc:
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
        "status": "pass" if health.get("status") == "ok" and profile in ("secure", "baseline") else "fail",
        "detail": f"Health status={health.get('status')!r}; profile={profile!r}",
    })
    expected_metadata = SECURITY_HEADERS if profile == "secure" else {}
    metadata_profile_ok = metadata.get("profile") == profile
    report["checks"].append({
        "id": "header-metadata-profile",
        "status": "pass" if metadata_profile_ok else "fail",
        "detail": f"Metadata profile={metadata.get('profile')!r}; health profile={profile!r}",
    })
    metadata_headers_ok = metadata.get("headers") == expected_metadata
    report["checks"].append({
        "id": "header-metadata-values",
        "status": "pass" if metadata_headers_ok else "fail",
        "detail": "Header metadata matches the declared profile." if metadata_headers_ok else "Header metadata does not match the declared profile.",
    })

    is_secure = profile == "secure"
    for name, expected in SECURITY_HEADERS.items():
        observed = headers.get(name)
        passed = observed == expected if is_secure else observed is None
        report["checks"].append({
            "id": "header:" + name.lower(),
            "status": "pass" if passed else "fail",
            "detail": (
                f"Observed {observed!r}; expected {expected!r}"
                if is_secure
                else f"Baseline observed {observed!r}; expected header absent"
            ),
        })

    failures = sum(check["status"] != "pass" for check in report["checks"])
    report["summary"] = {
        "total": len(report["checks"]),
        "passed": len(report["checks"]) - failures,
        "failed": failures,
    }
    report["status"] = "pass" if failures == 0 else "fail"
    if profile == "baseline":
        report["interpretation"] = (
            "The baseline intentionally omits the training security headers. "
            "PASS means the teaching baseline behaved as documented; it does not mean a production deployment is secure."
        )
    else:
        report["interpretation"] = (
            "PASS means this local lab matched the configured secure profile for the checks performed. "
            "It is not a full application security audit."
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
    parser = argparse.ArgumentParser(description="Assess a local STYX-LAB instance and save JSON/Markdown evidence.")
    parser.add_argument("--port", type=int, default=8766, help="Loopback port to assess (default: 8766).")
    parser.add_argument("--output-dir", default="reports", help="Output folder (default: reports).")
    args = parser.parse_args(argv)
    try:
        report = assess(args.port)
    except ValueError as exc:
        parser.error(str(exc))
    json_path, md_path = write_reports(report, args.output_dir)
    print(f"Assessment result: {report['status'].upper()}")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    if report["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
