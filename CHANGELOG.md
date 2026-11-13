# Changelog

## Unreleased

- Fixed terminal box alignment: layout now measures display cells, so emoji
  rows no longer push the right border one column out.
- Hardened the control-deck health probe and the assessment tool against JSON
  arrays, scalars, non-string profiles, and malformed HTTP responses instead of
  crashing on startup.
- Removed the trailing space from the `Server: STYX-LAB/1.0` response header.
- `lab.report` now reports an unwritable output directory as a clean error and
  exits with status 1 instead of printing a traceback.
- `install-to-repo.sh` now ships `README_TR.md`, the logo, `FUNDING.yml`, and
  itself, and refuses to run when source and target are the same repository.
- Updated CI to `actions/checkout@v7` and `actions/setup-python@v7` to clear
  the Node.js 20 deprecation warnings.

## v1.0.1

- Added a STYHQ-branded lock-to-unlocked startup sequence before the terminal dashboard.
- Added test coverage for animated TTY and fast non-interactive startup paths.
- Clarified that the splash is visual only and does not perform authentication.
- Removed generated Python cache files from the release archive.


## v1.0.0

- Added a local-only HTTP Security Headers training service.
- Added baseline and secure profiles, health and header metadata endpoints.
- Added the STYX-LAB / STYHQ terminal control deck and local status indicators.
- Added loopback-only assessment reports in JSON and Markdown.
- Expanded test coverage and cross-version CI configuration.
- Documented scope, limitations, remediation, and responsible use.

## v0.1.0

- Initialized project structure, methodology, and scenario template.
- Added initial test workflow and contribution/security guidance.
