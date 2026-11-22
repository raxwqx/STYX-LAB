# Changelog

## 1.1.0 - 2026-11-22

### Added

- New `weak` training profile: every demonstrated header is present, but with
  deliberately unsafe values (wildcard CSP with `unsafe-inline`/`unsafe-eval`,
  `sniff`, `unsafe-url`, wildcard permissions, and an invalid
  `X-Frame-Options`).
- New pure `lab.headers` module with severity-ranked findings, explanations,
  and remediation hints for the five training headers.
- Assessment reports now include `findings` and `finding_summary`, a Markdown
  findings table, and per-profile interpretation text.
- `--fail-on {none,low,medium,high,critical}` lets automation fail on findings
  while still writing the JSON/Markdown report.
- `--timeout` for the report CLI, validated to `0 < timeout <= 30` seconds.
- Control deck entry for the weak profile and live status for port `8767`.
- Tests for header analysis, weak-profile assessment, threshold behavior,
  timeout validation, and bounded response reads.

### Fixed

- The `Server` token now derives from the release version instead of drifting
  from a hardcoded `STYX-LAB/1.0`.
- An `unknown` health profile is no longer displayed as a healthy green state
  in the control deck.
- Local assessment responses are bounded to 1 MB, so a misbehaving local
  service cannot exhaust memory.
- Assessment timeout and port validation raise clean errors instead of
  surfacing raw socket or parsing exceptions.
- Fixed terminal box alignment: layout now measures display cells, so emoji
  rows no longer push the right border one column out.
- Hardened the control-deck health probe and the assessment tool against JSON
  arrays, scalars, non-string profiles, and malformed HTTP responses instead of
  crashing on startup.
- Removed the trailing space from the `Server` response header.
- `lab.report` now reports an unwritable output directory as a clean error and
  exits with status 1 instead of printing a traceback.
- `install-to-repo.sh` ships `README_TR.md`, the logo, `FUNDING.yml`, and
  itself, and refuses to run when source and target are the same repository.

### Changed

- Package metadata now declares a build backend, console scripts, classifiers,
  keywords, and project URLs.
- CI uses `actions/checkout@v7` and `actions/setup-python@v7` to clear the
  Node.js 20 deprecation warnings.

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
