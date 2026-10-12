<h1 align="center">🕷️ STYX-LAB</h1>

<p align="center">
  <strong>STYHQ // Local-First Cybersecurity Research &amp; Training</strong><br>
  Reproducible security exercises · Evidence-based reports · Animated terminal control deck
</p>

<p align="center">
  <a href="https://github.com/raxwqx/STYX-LAB/actions/workflows/tests.yml"><img alt="Tests" src="https://github.com/raxwqx/STYX-LAB/actions/workflows/tests.yml/badge.svg?branch=main"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&amp;logoColor=white">
  <img alt="Runtime dependencies" src="https://img.shields.io/badge/runtime%20dependencies-none-2ea44f">
  <a href="https://github.com/raxwqx/STYX-LAB/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <img alt="Platform" src="https://img.shields.io/badge/platform-Linux%20%7C%20Unix-lightgrey">
</p>

<p align="center"><em>A local security lab you can run, inspect, test, and learn from.</em></p>

Table of contents
- Overview
- Highlights
- STYHQ terminal control deck
- HTTP Security Headers lab
- Assessment and evidence reports
- Requirements
- Quick start
- Automated tests and continuous integration
- Architecture and project layout
- Security model and responsible use
- Limitations
- Troubleshooting
- Documentation
- Contributing
- Roadmap
- License
Overview
STYX-LAB is a local-first cybersecurity training project focused on the defensive workflow: define a security control, observe its behavior, validate the evidence, understand its limitations, and repeat the check after a change.
The project combines three practical pieces:
1. A terminal control deck branded as STYX-LAB / STYHQ. Its lock-opening startup sequence, neon panels, and status indicators provide a visual entry point to the lab.
2. A local HTTP Security Headers exercise with baseline and secure profiles, designed to make the effect of browser security headers easy to compare.
3. An assessment and reporting module that checks a running local STYX-LAB endpoint and exports the observed results in JSON and Markdown.
The emphasis is reproducibility and transparent evidence rather than a large feature count. The project is intentionally small, uses Python's standard library at runtime, and is designed so a contributor can run the lab without needing an external target.
Safety first: the included service binds only to the IPv4 loopback address, 127.0.0.1. STYX-LAB is educational software, not a production web server and not a complete security audit.

Highlights
Component	What it does
STYHQ terminal control deck	Shows a lock-to-unlocked startup animation in interactive terminals, then opens a numbered command menu.
Live service status	Checks the STYX-LAB health endpoint on the default secure and baseline ports.
Secure profile	Adds the five configured training security headers to responses.
Baseline profile	Deliberately omits those five headers so the response behaviors can be compared.
Health endpoint	Reports service status, selected profile, and tool version as JSON.
Header metadata endpoint	Exposes the expected header set for the selected training profile as JSON.
Local assessment	Checks a selected loopback port, validates responses and header behavior, and summarizes pass/fail results.
Evidence export	Writes a JSON report and a readable Markdown report.
Automated tests	Exercises HTTP behavior, report output, terminal startup, argument validation, and required project files.
Continuous integration	Configures GitHub Actions to run tests on Python 3.11, 3.12, and 3.13.


STYHQ terminal control deck
Launch the interactive interface from the repository root:
python3 lab/tui.py
In an interactive terminal, the app plays a short lock-opening sequence before displaying the dashboard. The animation progresses through locked, initializing, verifying, releasing, unlocked, and access-granted states. After the animation, the panel shows service status, Python version, local time, and the command menu.
The startup animation is visual only. It does not authenticate a user, unlock a real system, or provide an access-control boundary.
Menu options
Option	Action	What to expect
1	Launch secure profile	Starts the secure HTTP training service on the chosen local port.
2	Launch baseline profile	Starts the baseline comparison service on the chosen local port.
3	Run automated tests	Runs the project's unittest suite and returns to the menu.
4	Run local assessment + export reports	Checks a selected local STYX-LAB service and writes JSON and Markdown reports.
5	Read scenario guide	Displays the HTTP Security Headers scenario documentation in the terminal.
0	Exit control deck	Closes the interface.


The dashboard uses health responses, not just an open TCP port, to determine whether a service appears to be a STYX-LAB instance. The status display checks the default ports 8766 and 8765. If you start a service on a custom port, use that port when running an assessment.
Animation and non-interactive mode
When output is not attached to an interactive terminal, STYX-LAB skips the deliberate animation delays and prints a concise boot notice. This keeps automated tests and log output predictable. You can explicitly disable the animation:
STYXLAB_NO_ANIMATION=1 python3 lab/tui.py
Color output respects the standard NO_COLOR environment variable.
HTTP Security Headers lab
The included server uses Python's built-in HTTP server classes. It does not require a web framework or additional runtime packages.
Profiles
Baseline is a teaching profile that intentionally omits the five headers under study. A passing baseline assessment means the lab behaved as documented; it does not mean the baseline is a safe production configuration.
Secure applies the configured training header values. The profile demonstrates the controls and their observable effect. It is not a claim that every application is secure because it sends these headers.
Security headers covered
Header	Configured value or behavior	Learning purpose
Content-Security-Policy	default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'	Demonstrates resource-source restrictions and framing policy. A real application must review its resource requirements before adopting a policy.
X-Content-Type-Options	nosniff	Tells compatible browsers not to MIME-sniff the response.
Referrer-Policy	strict-origin-when-cross-origin	Demonstrates limiting referrer information sent on cross-origin requests.
Permissions-Policy	Disables camera, microphone, and geolocation for the page	Shows how browser capabilities can be restricted.
X-Frame-Options	DENY	Demonstrates a framing restriction for compatible browsers.


Both profiles also return Cache-Control: no-store. The exercise uses plain HTTP on loopback, so it does not set HSTS. HSTS belongs in a properly configured HTTPS deployment, not as a pretend fix for a local plain-HTTP exercise.
Endpoints
Endpoint	Method	Purpose
/	GET	Serves a small HTML page identifying the active training profile.
/health	GET	Returns JSON with status, profile, and version.
/api/headers	GET	Returns JSON metadata describing the active profile and configured training headers.
Any unknown path	GET	Returns HTTP 404 with a JSON error body.


Run the secure profile
Start the service in one terminal:
python3 lab/web/security_headers_lab.py --profile secure --port 8766
Inspect the page response from another terminal:
curl -i http://127.0.0.1:8766/
Check health:
curl -i http://127.0.0.1:8766/health
Inspect profile metadata:
curl -i http://127.0.0.1:8766/api/headers
The health response contains a JSON object similar to:
{
  "status": "ok",
  "profile": "secure",
  "version": "1.0.1"
}
The exact header ordering and server date are handled by the HTTP server and may vary. Compare header names and values, not their printed order.
Compare the baseline and secure profiles
In a separate terminal, start the baseline profile:
python3 lab/web/security_headers_lab.py --profile baseline --port 8765
Then inspect both responses:
curl -i http://127.0.0.1:8765/
curl -i http://127.0.0.1:8766/
The five training headers should be absent from the baseline response and present with the configured values in the secure response. Stop each server with Ctrl+C when finished.
Assessment and evidence reports
The assessment module checks a running local STYX-LAB instance on an explicitly selected port. It contacts only 127.0.0.1; it does not scan a network, resolve hostnames, or contact external systems.
Run an assessment
Keep the service running, then execute:
python3 -m lab.report --port 8766
Or choose a separate output directory:
python3 -m lab.report --port 8766 --output-dir reports/demo
By default, the module writes:
- reports/latest-assessment.json — structured results suitable for inspection or later processing.
- reports/latest-assessment.md — a readable report with the result, scope, profile, individual checks, and summary.
The reports directory is generated at runtime and should be reviewed before committing or publishing a report. Reports contain a timestamp and a local target port.
What the assessment checks
The assessment validates that the selected endpoint responds like the STYX-LAB service, checks health/profile information, compares declared header metadata to the selected profile, and checks the five security headers against the configured expectations.
The JSON report includes a schema version, tool version, creation timestamp, target, scope, per-check status and detail, overall status, and a summary of passed and failed checks when those checks can be completed.
Possible outcomes include:
- PASS: the local lab matched the expected behavior for the checks performed.
- FAIL: one or more responses or header values did not match the expected behavior.
- UNAVAILABLE: the selected endpoint did not return the required valid local responses.
A baseline can correctly receive PASS because that profile is deliberately supposed to omit the five training headers. Read the profile and interpretation fields rather than treating PASS as a universal security rating.
Evidence, not a guarantee: an assessment report records only the checks implemented by this training project against the selected local lab. It does not certify an application, host, or network as secure.

Requirements
- Python 3.11 or newer.
- curl is optional and used for manual HTTP inspection.
- No third-party Python packages are required to run the application or unit tests.
- A terminal is recommended for the full color and animation experience. Non-interactive execution is supported for testing and automation.
Quick start
Clone the repository:
git clone https://github.com/raxwqx/STYX-LAB.git
cd STYX-LAB
Launch the control deck:
python3 lab/tui.py
Run the test suite directly:
python3 -m unittest discover -s tests -v
Applying a release ZIP to an existing checkout
If you are applying a release ZIP to an existing Git checkout, extract the archive and run the included installer with the path to that checkout:
bash /path/to/STYX-LAB-v1.0.1/install-to-repo.sh /path/to/STYX-LAB
The helper is designed to back up files it replaces, preserve the target checkout's .git history, and run validation after copying. Read the script before using it, keep your own backup of important work, and inspect Git status and test results after installation. A regular Git clone does not need this helper.
Automated tests and continuous integration
Run the suite locally:
python3 -m unittest discover -s tests -v
Compile the application and tests:
python3 -m compileall -q lab tests
The test suite covers:
- Required project files and Python source parsing.
- Loopback binding and invalid profile/port handling.
- Secure header values and baseline header absence.
- Health and header metadata endpoints.
- Unknown-path behavior.
- Assessment behavior against live test servers and unavailable ports.
- JSON and Markdown report generation.
- Terminal startup behavior, lock-opening states, STYHQ branding, and exit flow.
GitHub Actions is configured to run the test suite and Python compile check on Python 3.11, 3.12, and 3.13. The Tests badge at the top links to the workflow page, where the actual result for each workflow run can be inspected. A configured matrix is not the same as a successful run; use the Actions page to confirm the latest run results.
Architecture and project layout
STYX-LAB separates the terminal interface, local HTTP service, report generation, documentation, and tests.
STYX-LAB/
├── .github/
│   └── workflows/
│       └── tests.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── methodology/
│   │   └── README.md
│   └── scenarios/
│       ├── TEMPLATE.md
│       └── web-security-headers.md
├── lab/
│   ├── __init__.py
│   ├── report.py
│   ├── tui.py
│   └── web/
│       ├── __init__.py
│       └── security_headers_lab.py
├── tests/
│   ├── test_project_structure.py
│   ├── test_report.py
│   ├── test_security_headers_lab.py
│   └── test_tui.py
├── CHANGELOG.md
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── SECURITY.md
└── install-to-repo.sh
Component responsibilities
- lab/tui.py — terminal presentation, startup animation, status checks, menu actions, and interactive navigation.
- lab/web/security_headers_lab.py — loopback-only HTTP server and training endpoints.
- lab/report.py — local assessment logic and JSON/Markdown report generation.
- tests/ — regression tests for the implemented behaviors.
- .github/workflows/tests.yml — automated test and compile checks.
- docs/ — scenario instructions, methodology, architecture, and reusable template.
For component boundaries and data flow, see [Architecture](docs/ARCHITECTURE.md).
Security model and responsible use
STYX-LAB is designed for local defensive training.
- The HTTP server binds to IPv4 loopback rather than a network interface.
- Assessment requests use the loopback address and a port selected by the user.
- The included checks target the STYX-LAB training service, not arbitrary third-party systems.
- The lock-opening animation is branding only and is not a security mechanism.
- No real credentials are required for the included scenario.
- A passing report applies only to the listed checks and the selected lab instance.
Run the exercises only in environments you own or are explicitly authorized to test. Do not use the project to probe systems without permission, and do not expose the built-in training server to the public internet.
For repository vulnerability reporting guidance, see [SECURITY.md](SECURITY.md).
Limitations
STYX-LAB is an early, intentionally narrow training platform. The current release demonstrates one web-security topic: HTTP security headers.
It does not currently provide:
- A full web application vulnerability scanner.
- A general-purpose network scanner or packet analyzer.
- Browser-based integration tests across multiple browsers.
- Authentication or user accounts.
- A production-ready HTTP server.
- A guarantee that a real application is secure because its headers match this lab's values.
- A replacement for an authorized professional security review.
The report module evaluates the selected local STYX-LAB endpoint. It does not assess arbitrary URLs or remote targets. The configured Content Security Policy is a teaching policy and must be adapted and tested before use in a real application.
These boundaries are deliberate: the included scenario should be easy to run, inspect, test, and understand before the project grows to cover additional scenarios.
Troubleshooting
The terminal says the port is already in use
A service may already be listening on the requested port. Keep the existing service if it is the one you intend to use, or start another instance on a different available port and pass that port to the assessment command.
The dashboard shows a service as offline
The dashboard uses the STYX-LAB health response, not just an open TCP port. Start the corresponding profile and wait for it to print its local URL. If you used a non-default port, remember that the dashboard's fixed status display still checks 8766 and 8765.
The assessment returns UNAVAILABLE
Confirm that the intended STYX-LAB profile is running, check the port number, then inspect the JSON and Markdown reports for the recorded error. The assessment stays local and does not search for another service automatically.
Colors or animation do not appear
The lock animation and ANSI colors are intended for interactive terminals. Non-interactive execution and the STYXLAB_NO_ANIMATION environment variable disable the animated startup sequence. NO_COLOR disables color formatting.
Tests pass locally but a CI workflow fails
Open the GitHub Actions workflow linked by the Tests badge. Check the Python version and complete error output for the failing matrix job before claiming that the project passes on that version.
Documentation
- [Architecture and data flow](docs/ARCHITECTURE.md)
- [HTTP Security Headers scenario](docs/scenarios/web-security-headers.md)
- [Research methodology](docs/methodology/README.md)
- [Scenario template](docs/scenarios/TEMPLATE.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Project roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Citation metadata](CITATION.cff)
Contributing
Contributions are welcome when they improve correctness, reproducibility, accessibility, test coverage, or defensive learning value.
Before proposing a new scenario:
1. Define the objective and local scope.
2. State prerequisites and expected behavior.
3. Provide repeatable steps and evidence to collect.
4. Explain risk, remediation, limitations, and cleanup.
5. Add tests for stable behavior where practical.
Run the local test and compile checks before submitting a change. Keep changes focused, do not include credentials or personal data, and describe what your tests actually verified. See [CONTRIBUTING.md](CONTRIBUTING.md).
Roadmap
The roadmap lists potential future improvements rather than promising unfinished features. Current candidates include another self-contained defensive web scenario, optional report metadata, accessibility and terminal-width improvements, and example reports generated by tests.
See [ROADMAP.md](ROADMAP.md) for the maintained list.
License
STYX-LAB is released under the MIT License. See LICENSE.
