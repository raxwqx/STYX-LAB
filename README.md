# 🕷️ STYX-LAB

**Local-first cybersecurity research and training platform · v1.0.1.**

STYX-LAB teaches defensive security through local experiments, explicit
expected outcomes, automated checks, and evidence-based JSON/Markdown reports.

> **Safety first:** lab services bind only to `127.0.0.1`. This is training
> software, not a production server or a full security audit.

## Features

- **STYX-LAB v1.0.1 / STYHQ terminal control deck:** a lock-to-unlocked startup
  sequence, neon panels, live health-based service states, and a numbered menu.
  The intro is visual only; it does not perform authentication.
- **HTTP Security Headers lab:** baseline and secure comparison profiles.
- **Health and metadata endpoints:** `/health` and `/api/headers`.
- **Local assessment reports:** generate JSON and Markdown evidence about a
  running loopback lab instance.
- **Automated tests:** validate HTTP behavior, header values, input handling,
  loopback binding, report rendering, and required project files.
- **GitHub Actions:** test across supported Python versions.

## Requirements

- Python 3.11 or newer
- `curl` for optional manual checks
- No third-party runtime dependencies

## Quick start

    git clone https://github.com/raxwqx/STYX-LAB.git
    cd STYX-LAB
    python3 lab/tui.py

The terminal menu launches the secure or baseline profile, runs automated
checks, generates a local assessment report, and opens the scenario guide.
On a real terminal, startup plays a short lock-opening animation before the
dashboard. Non-interactive runs skip the animation to keep tests fast.

## Apply a release ZIP to an existing checkout

If you are applying the provided release bundle to an existing Git checkout,
extract the ZIP and run its `install-to-repo.sh` helper with the checkout path.
It makes a temporary backup of files it replaces, preserves the `.git` history,
then runs the automated tests and compile check; it rolls back copied files if
validation fails. For a normal Git clone, no installer is needed.

## Run manually

Start the secure profile:

    python3 lab/web/security_headers_lab.py --profile secure --port 8766

In another terminal:

    curl -i http://127.0.0.1:8766/
    curl -i http://127.0.0.1:8766/health
    curl -i http://127.0.0.1:8766/api/headers

## Generate evidence reports

Keep the secure profile running, then run from the repository root:

    python3 -m lab.report --port 8766

Reports are written to `reports/latest-assessment.json` and
`reports/latest-assessment.md`. Reports document observed local behavior;
they do not claim to prove that an entire application is secure.

## Test

    python3 -m unittest discover -s tests -v

## Scenario and methodology

- [HTTP Security Headers scenario](docs/scenarios/web-security-headers.md)
- [Research methodology](docs/methodology/README.md)
- [Scenario template](docs/scenarios/TEMPLATE.md)

## Project layout

    lab/web/       Local HTTP security headers server
    lab/report.py  Loopback-only assessment and evidence reporting
    lab/tui.py     STYX-LAB / STYHQ terminal control deck
    docs/          Methodology and scenario guides
    tests/         Automated regression tests
    .github/       GitHub Actions workflow

## Responsible use

Only use the lab in controlled environments. Do not test systems without
permission. The service intentionally binds to loopback and should not be
exposed publicly.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
Licensed under MIT; see [LICENSE](LICENSE).
