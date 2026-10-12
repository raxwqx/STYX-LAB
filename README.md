STYX-LAB 🕷️
Local-first cybersecurity research and training laboratory.
STYX-LAB combines a terminal control deck branded STYHQ, a local HTTP Security Headers exercise, and evidence-based JSON/Markdown reports. It is built for repeatable defensive learning: inspect a control, compare expected and observed behavior, and keep the result as evidence.





Safety first: The included HTTP lab binds only to 127.0.0.1. STYX-LAB is educational software, not a production web server or a complete security audit.

Contents
- Why STYX-LAB
- Capabilities
- STYHQ terminal control deck
- HTTP Security Headers lab
- Assessment and reports
- Installation
- Quick start
- Usage examples
- Testing and CI
- Architecture
- Security scope and limitations
- Troubleshooting
- Documentation
- Contributing
- Roadmap
- License
Why STYX-LAB
Security controls are easier to understand when their behavior is observable and repeatable. STYX-LAB keeps its first exercise intentionally small: run two local HTTP profiles, compare the response headers, validate the service's metadata, and export the checks as a report.
- Local-first: the included web service and assessment target use IPv4 loopback (127.0.0.1).
- Reproducible: baseline and secure profiles provide a controlled comparison.
- Evidence-focused: the assessment records per-check results and writes JSON and Markdown reports.
- Inspectable: the project uses Python's standard library at runtime, with no third-party runtime dependencies.
- Testable: automated tests cover service behavior, reporting, and the terminal interface.
- Clear boundaries: reports explain that passing the lab checks is not a guarantee that an application is secure.
Capabilities
Area	Current capability
Terminal interface	STYX-LAB / STYHQ branded control deck with a lock-opening startup animation in interactive terminals.
Service status	Health-based status checks for the default secure and baseline ports.
Web training	Baseline and secure HTTP Security Headers profiles.
HTTP endpoints	HTML home page, JSON health endpoint, JSON header metadata endpoint, and JSON 404 response.
Assessment	Checks service reachability, profile metadata, and the five configured security headers.
Reports	Structured JSON and readable Markdown output.
Validation	Unit and integration tests plus Python compile checks in GitHub Actions.


STYHQ terminal control deck
Start the control deck from the repository root:
python3 lab/tui.py
In an interactive terminal, startup displays a short sequence of states:
🔒  GATE LOCKED
🔒  INITIALIZING
🔒  VERIFYING MODULES
🔐  RELEASING LATCH
🔓  GATE UNLOCKED
🔓  ACCESS GRANTED

STYX-LAB // CYBERSECURITY CONTROL DECK
STYHQ // SECURITY HQ
The lock animation is a visual introduction only. It does not authenticate users or provide a security boundary. When output is non-interactive, the interface skips animation delays to keep tests and logs predictable.
Menu reference
Key	Action	Description
1	Launch secure profile	Starts the local server with the configured training headers.
2	Launch baseline profile	Starts the comparison server without those five training headers.
3	Run automated tests	Executes the test suite and reports the test process result.
4	Run local assessment + export reports	Checks the selected local STYX-LAB port and writes reports.
5	Read scenario guide	Displays the HTTP Security Headers exercise in the terminal.
0	Exit control deck	Closes the terminal interface.


The dashboard checks the health endpoint on default ports 8766 (secure) and 8765 (baseline). If you start a server on a custom port, provide that port when running the assessment.
Disable the startup animation when desired:
STYXLAB_NO_ANIMATION=1 python3 lab/tui.py
Color output respects the NO_COLOR environment variable.
HTTP Security Headers lab
The server is implemented with Python's built-in HTTP server classes. It does not need Flask, FastAPI, or other third-party runtime packages.
Profiles
- secure adds the five configured browser security headers.
- baseline deliberately omits those five headers so you can observe the difference.
A passing baseline assessment means the teaching profile behaved as documented. It does not mean the baseline configuration is suitable for production.
Headers demonstrated
Header	Configured value in secure	Learning objective
Content-Security-Policy	default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'	Demonstrates content-source restrictions and a framing policy.
X-Content-Type-Options	nosniff	Demonstrates disabling MIME sniffing in compatible browsers.
Referrer-Policy	strict-origin-when-cross-origin	Demonstrates controlling referrer information sent across origins.
Permissions-Policy	camera=(), microphone=(), geolocation=()	Demonstrates disabling selected browser capabilities for the page.
X-Frame-Options	DENY	Demonstrates a framing restriction for compatible browsers.


Both profiles also set Cache-Control: no-store. The exercise uses plain HTTP on loopback and intentionally does not set HSTS; HSTS is intended for appropriately configured HTTPS deployments. These headers complement secure coding and must be selected and tested for the needs of a real application.
HTTP endpoints
Endpoint	Method	Purpose
/	GET	Serves the local training page and identifies the selected profile.
/health	GET	Returns JSON with service status, profile, and version.
/api/headers	GET	Returns JSON metadata for the active profile and expected training headers.
Unknown path	GET	Returns HTTP 404 with a JSON error.


Assessment and reports
The assessment module checks one explicitly selected local STYX-LAB endpoint. It contacts 127.0.0.1 only: it does not scan networks, resolve remote hostnames, or contact external targets.
What it checks
For a valid STYX-LAB response, the assessment checks:
1. Whether the header-metadata and health endpoints respond.
2. Whether the health status and profile are valid.
3. Whether the metadata profile agrees with the health profile.
4. Whether the metadata header map matches the selected profile.
5. Whether each of the five headers has its expected value, or is absent in the baseline profile.
A complete response normally produces nine individual checks. If the endpoint is unavailable or returns invalid JSON, the report records the problem instead of treating the assessment as successful.
Generate reports
Start a profile first, for example:
python3 lab/web/security_headers_lab.py --profile secure --port 8766
Then, from a second terminal at the repository root, run:
python3 -m lab.report --port 8766
Choose a separate output directory when you want to keep a demo report apart from the latest report:
python3 -m lab.report --port 8766 --output-dir reports/demo
By default, reports are written to:
- reports/latest-assessment.json — machine-readable metadata and individual check results.
- reports/latest-assessment.md — a human-readable summary, scope, observed evidence, and per-check results.
The reports/ directory is generated at runtime. Inspect reports before sharing or committing them; they include a timestamp and local target port.
Interpret the outcome correctly
- PASS means the local lab matched the expected behavior for the checks performed.
- FAIL means one or more returned values did not match expectations.
- UNAVAILABLE means the required local service response could not be obtained or parsed.
The baseline profile can correctly receive PASS because its documented behavior is to omit the five training headers. Always read the profile and interpretation in the report. This output is evidence about the training endpoint, not a full audit or certification of a real application.
Example terminal output
Illustrative output from a successful assessment; timestamps and the actual target port vary by run:
Assessment result: PASS
JSON report: reports/latest-assessment.json
Markdown report: reports/latest-assessment.md
An abbreviated JSON summary can look like this:
{
  "target": "http://127.0.0.1:8766",
  "profile": "secure",
  "status": "pass",
  "summary": {
    "total": 9,
    "passed": 9,
    "failed": 0
  }
}
This is an example of the report shape, not a result collected from your machine. The live report files contain the actual checks and timestamp from your own run.
Installation
Requirements
- Python 3.11 or newer.
- curl is optional and used only for manual response inspection.
- No third-party Python packages are required for the application or unit tests.
- A terminal is recommended for the full color and animation experience.
Option A: Clone with Git
git clone https://github.com/raxwqx/STYX-LAB.git
cd STYX-LAB
Option B: Download the source ZIP
Download the latest source ZIP from the main branch
Extract the archive, enter the extracted STYX-LAB directory, and follow the quick-start instructions below. The GitHub source ZIP is a snapshot of the branch; it is not a compiled binary release.
Quick start
Launch the terminal control deck:
python3 lab/tui.py
Run the automated suite directly:
python3 -m unittest discover -s tests -v
Compile-check application and test sources:
python3 -m compileall -q lab tests
Usage examples
Run the secure profile
In terminal 1:
python3 lab/web/security_headers_lab.py --profile secure --port 8766
In terminal 2:
curl -i http://127.0.0.1:8766/
curl -i http://127.0.0.1:8766/health
curl -i http://127.0.0.1:8766/api/headers
Compare against baseline
In a separate terminal:
python3 lab/web/security_headers_lab.py --profile baseline --port 8765
Inspect both responses:
curl -i http://127.0.0.1:8765/
curl -i http://127.0.0.1:8766/
Compare the header names and values rather than their order. Stop each running service with Ctrl+C. If a port is already in use, choose another available port and use it consistently in the matching assessment command.
Run a report for baseline
python3 -m lab.report --port 8765
A baseline PASS only confirms the deliberate teaching behavior of that profile; it is not a production security recommendation.
Testing and CI
Run the complete test suite:
python3 -m unittest discover -s tests -v
Run a syntax/bytecode compile check:
python3 -m compileall -q lab tests
The test suite covers the HTTP profiles and headers, loopback binding, health and metadata endpoints, invalid profile/port values, unknown paths, assessment results, JSON/Markdown report writing, and terminal interface startup and animation behavior.
GitHub Actions is configured to run tests and the compile check with Python 3.11, 3.12, and 3.13 on pushes and pull requests. Use the Actions page to confirm the current result for each matrix job; a configured workflow is not itself proof that every run passed.
Architecture
STYX-LAB keeps the user interface, HTTP lab, and report generation in separate modules:
STYX-LAB/
├── .github/workflows/tests.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── methodology/README.md
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
Module	Responsibility
lab/tui.py	Startup sequence, terminal panels, health-based status display, command routing, and interactive navigation.
lab/web/security_headers_lab.py	Loopback-only HTTP server, training profiles, and HTTP endpoints.
lab/report.py	Local endpoint assessment and JSON/Markdown evidence export.
tests/	Regression tests for the currently implemented behavior.
.github/workflows/tests.yml	Automated test and compile checks.
docs/	Scenario instructions, methodology, and architecture notes.


See [Architecture](docs/ARCHITECTURE.md) for component boundaries and data flow.
Security scope and limitations
STYX-LAB is currently a focused training platform for one web-security topic: HTTP Security Headers. The current release is not:
- a full web application vulnerability scanner;
- a general-purpose network scanner or packet analyzer;
- a browser-based cross-browser test framework;
- an authentication system or access-control gate;
- a production-ready HTTP server;
- a guarantee that an application is secure because its headers match the training profile;
- a replacement for an authorized professional security review.
The included server binds to 127.0.0.1, and assessment requests are limited to that loopback host. Do not expose the training service publicly or use the project to probe systems without authorization. The lock animation is branding only, not an access-control feature.
For repository vulnerability reporting guidance, see [SECURITY.md](SECURITY.md).
Troubleshooting
A port is already in use
An existing process may already be listening. Keep it if it is the intended lab service, or select another available port and pass the same port to the assessment command. Avoid stopping processes blindly; first identify what is using the port.
The dashboard shows a lab as offline
The dashboard uses the service health endpoint on the default ports 8766 and 8765. Start the chosen profile and wait for it to print its local URL. Services started on a custom port are not shown in those fixed dashboard indicators, but can still be assessed by specifying their port.
The assessment is UNAVAILABLE
Confirm the service is running, check the specified port, then open reports/latest-assessment.json or reports/latest-assessment.md and inspect the recorded error. The assessment does not search for another service automatically.
Colors or animation are missing
Run from an interactive terminal. Non-interactive mode and STYXLAB_NO_ANIMATION=1 skip startup animation; NO_COLOR disables ANSI color formatting.
A CI job fails while local tests pass
Open the Actions page, select the failed workflow run, and inspect the Python matrix version and full test output before claiming compatibility for that run.
Documentation
- [Architecture and data flow](docs/ARCHITECTURE.md)
- [HTTP Security Headers scenario](docs/scenarios/web-security-headers.md)
- [Research methodology](docs/methodology/README.md)
- [Scenario template](docs/scenarios/TEMPLATE.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Citation metadata](CITATION.cff)
Contributing
Contributions are welcome when they improve correctness, reproducibility, accessibility, test coverage, or defensive learning value.
Before adding a scenario:
1. Define the objective, prerequisites, and local scope.
2. State expected behavior before writing validation checks.
3. Provide repeatable commands and the evidence to collect.
4. Explain risk, remediation, limitations, and cleanup.
5. Add automated tests for stable behavior where practical.
Run the test suite and compile check before submitting. Keep changes focused, do not include credentials or personal data, and describe what your tests actually verified. See [CONTRIBUTING.md](CONTRIBUTING.md).
Roadmap
Future candidates—not current features—include another self-contained defensive web scenario, optional report metadata, improved accessibility and terminal-width handling, and example reports generated by tests. See [ROADMAP.md](ROADMAP.md) for the maintained plan.
License
STYX-LAB is released under the MIT License. See LICENSE for the full text.
<p align="center"><strong>STYHQ // STYX-LAB</strong><br>Stay sharp. Stay defensive. 🛡️</p>
