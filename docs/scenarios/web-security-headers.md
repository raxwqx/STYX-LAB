# Scenario: HTTP Security Headers

## Objective

Compare baseline and secure HTTP responses, inspect browser security headers,
and generate a local evidence report.

## Scope and safety

- The training server binds only to `127.0.0.1`.
- Python standard library only; no third-party packages required.
- This is an educational HTTP service, not production software.
- The report tool only contacts IPv4 loopback at the port you specify.

## Run the baseline profile

From the repository root, run:

    python3 lab/web/security_headers_lab.py --profile baseline --port 8765

In another terminal:

    curl -i http://127.0.0.1:8765/

Expected: HTTP 200 and the five training security headers absent.

## Run the secure profile

In a separate terminal:

    python3 lab/web/security_headers_lab.py --profile secure --port 8766

Inspect the response and health endpoint:

    curl -i http://127.0.0.1:8766/
    curl -i http://127.0.0.1:8766/health
    curl -i http://127.0.0.1:8766/api/headers

The secure response should include:

| Header | Purpose |
|---|---|
| `Content-Security-Policy` | Restricts resource sources and framing. |
| `X-Content-Type-Options: nosniff` | Prevents content-type guessing. |
| `Referrer-Policy` | Controls browser referrer information. |
| `Permissions-Policy` | Restricts the listed browser features. |
| `X-Frame-Options: DENY` | Adds a framing restriction for compatible browsers. |

## Generate evidence reports

With the secure profile running:

    python3 -m lab.report --port 8766

This writes `reports/latest-assessment.json` and
`reports/latest-assessment.md`. The assessment reports observed behavior;
it is not a full application security audit. An unavailable service produces
an `unavailable` result and a non-zero exit code.

## Risk and remediation

Missing browser security headers can weaken protections depending on the
application and its other controls. Choose policies appropriate for the real
application, verify required functionality, and re-test after changes.
Headers complement secure coding and do not replace it. HSTS is not set in
this plain-HTTP loopback exercise; it is intended for properly configured
HTTPS deployments.

## Automated re-test

    python3 -m unittest discover -s tests -v

Review failures rather than assuming that a configuration is correct.

## Cleanup and limitations

Stop services with `Ctrl+C`. Do not expose the training server publicly. The
example is not a production web framework or a complete security assessment.
