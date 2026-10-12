# Architecture

STYX-LAB is intentionally local-first and dependency-free at runtime.

## Components

- `lab/web/security_headers_lab.py` hosts an HTTP exercise on IPv4 loopback.
- `lab/tui.py` is the interactive STYX-LAB / STYHQ terminal control deck. Its
  lock-to-unlocked splash is a visual startup sequence only, not authentication.
  It checks lab health endpoints instead of treating any open port as healthy.
- `lab/report.py` checks one explicitly selected loopback port and produces
  JSON and Markdown evidence reports. It does not resolve or contact remote hosts.
- `tests/` validates HTTP behavior, report output, UI startup, and source layout.
- `.github/workflows/tests.yml` runs regression tests on supported Python versions.

## Boundaries

The server binds to `127.0.0.1` only. The assessment module hard-codes the same
loopback host. The report is evidence about the specific training endpoint,
not a guarantee that a complete application is secure.

## Data flow

1. A user starts a local lab profile from the terminal menu or CLI.
2. The user observes HTTP responses manually or through the report module.
3. A report records observed headers, health metadata, check results, timestamp,
   target port, and summary.
4. Automated tests validate baseline and secure profile behavior.
