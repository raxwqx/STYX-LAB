STYX-LAB 🕷️
Local-first cybersecurity training lab for HTTP security headers, written in Python.
    
STYX-LAB is a small defensive security lab for exploring HTTP Security Headers through two local web-server profiles. It includes a terminal control deck, a deliberately minimal baseline profile, a secure training profile, and an assessment tool that exports evidence-backed JSON and Markdown reports.
It is designed for cybersecurity learning, repeatable local experiments, and understanding how browser security headers differ between two known configurations. The included service binds to 127.0.0.1 and the assessment tool evaluates the local STYX-LAB service only.
Analyst note: A passing assessment means the selected lab profile behaved as expected for the checks performed. It is not proof that a real application is secure, and the baseline profile is intentionally not a production configuration.
Contents
- Why STYX-LAB
- Capabilities
- HTTP Security Headers lab
- How it works
- Requirements
- Build and install
- Quick start
- Control deck reference
- Profiles and endpoints
- Assessment and reports
- Testing and development
- Architecture
- Limitations
- Responsible use and data handling
- Roadmap ideas
- License
Why STYX-LAB
HTTP security headers are easier to learn when their behavior can be compared and checked in a controlled environment. STYX-LAB keeps the exercise intentionally focused: run a profile, inspect the response, compare its headers with the expected configuration, and save the results for later review.
- Local-first: the included service uses IPv4 loopback (127.0.0.1).
- Side-by-side learning: compare a secure profile with a baseline profile.
- Evidence-focused: each assessment records individual checks and writes JSON and Markdown reports.
- Easy to run: uses the Python standard library and has no third-party runtime dependencies.
- Testable: automated tests cover the web service, assessment logic, reporting, and terminal interface.
- Clear scope: the project is a training lab, not a general-purpose web vulnerability scanner.
Capabilities
Area	Current capability
Terminal interface	STYHQ-branded terminal control deck with menu-driven actions and an optional startup animation.
Web lab	Local HTTP server with secure and baseline profiles.
Security headers	Demonstrates five browser-related response headers and their configured values.
Endpoints	HTML home page, JSON health endpoint, JSON header metadata endpoint, and JSON 404 response.
Assessment	Checks local service availability, profile metadata, header metadata, and the five configured headers.
Reports	Exports a machine-readable JSON report and a human-readable Markdown report.
Quality checks	Unit and integration tests plus a Python compile check in GitHub Actions.


HTTP Security Headers lab
The lab uses Python's built-in HTTP server functionality. Flask, FastAPI, and other third-party web frameworks are not required.
Profiles
Profile	Behavior	Intended use
secure	Sends the five configured training headers.	Inspect an example header configuration and compare observed values with expectations.
baseline	Deliberately omits those five training headers.	See how the responses differ when the selected headers are absent.


Both profiles set Cache-Control: no-store. The baseline profile is intentionally designed for comparison; it should not be treated as a recommended production setup. The lab uses plain HTTP on loopback and does not configure HSTS, which is intended for appropriately configured HTTPS deployments.
Headers demonstrated
Header	secure profile value	Learning objective
Content-Security-Policy	default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'	Demonstrates restricting content sources and framing.
X-Content-Type-Options	nosniff	Demonstrates disabling MIME sniffing in compatible browsers.
Referrer-Policy	strict-origin-when-cross-origin	Demonstrates controlling referrer information sent across origins.
Permissions-Policy	camera=(), microphone=(), geolocation=()	Demonstrates disabling selected browser capabilities.
X-Frame-Options	DENY	Demonstrates a framing restriction for compatible browsers.


These headers are only one part of web security. A real application needs a policy designed for its assets, functionality, deployment, and threat model. Copying the example values without testing application behavior is not a substitute for secure design and review.
How it works
Start the secure or baseline profile
                 |
                 v
      Local HTTP service on loopback
                 |
                 v
        Health and header endpoints
                 |
                 v
     Assessment requests the local lab
                 |
                 v
       Compare observed and expected data
                 |
                 v
       Record per-check results and evidence
                 |
             /       \\
            v         v
       JSON report  Markdown report
The terminal control deck provides shortcuts for launching a profile, running tests, starting an assessment, and reading the scenario guide. The assessment logic is separate from the terminal interface so it can also be run directly from the command line.
Requirements
- Python 3.11 or newer.
- Linux or another environment with a supported Python 3.11+ installation.
- A terminal for the control deck and command-line workflows.
- curl is optional and can be used to inspect HTTP responses manually.
- No third-party Python runtime packages are required.
Build and install
STYX-LAB is a Python project and does not need a compiled build step or a package installation for the documented workflows.
Clone the repository
git clone https://github.com/raxwqx/STYX-LAB.git
cd STYX-LAB
Download the source ZIP
Download the latest source ZIP from GitHub
Extract the ZIP archive, open a terminal in the extracted STYX-LAB directory, and continue with the quick start below. The ZIP is a source snapshot, not a precompiled release.
Quick start
1. Start the terminal control deck
python3 lab/tui.py
Use the menu to launch a profile, run tests, create a report, or read the scenario guide.
2. Start the secure profile directly
python3 lab/web/security_headers_lab.py --profile secure --port 8766
The server reports its local address. Keep this terminal open while using the service.
3. Inspect the response
Open a second terminal in the repository directory and run:
curl -i http://127.0.0.1:8766/
curl -i http://127.0.0.1:8766/health
curl -i http://127.0.0.1:8766/api/headers
4. Generate an assessment report
python3 -m lab.report --port 8766
The report is written to reports/latest-assessment.json and reports/latest-assessment.md by default. Stop the server with Ctrl+C when the exercise is complete.
Control deck reference
Run the terminal interface from the repository root:
python3 lab/tui.py
Key	Action	Description
1	Launch secure profile	Starts the local server with the configured training headers.
2	Launch baseline profile	Starts the comparison server without the five training headers.
3	Run automated tests	Executes the test suite and displays the result.
4	Run local assessment and export reports	Assesses the selected local STYX-LAB port and writes reports.
5	Read scenario guide	Displays the HTTP Security Headers exercise.
0	Exit	Closes the terminal interface.


The dashboard checks the default secure port 8766 and baseline port 8765. If you launch a service on a custom port, provide the same port when running the assessment.
The startup lock animation is visual branding only. It does not authenticate users or create an access-control boundary. To skip the animation, run:
STYXLAB_NO_ANIMATION=1 python3 lab/tui.py
Set NO_COLOR in the environment to disable ANSI color output.
Profiles and endpoints
The web server supports a small set of local endpoints:
Endpoint	Method	Purpose
/	GET	Serves the training page and identifies the selected profile.
/health	GET	Returns JSON service status, profile, and version information.
/api/headers	GET	Returns JSON metadata for the active profile and expected training headers.
Unknown path	GET	Returns a JSON error with HTTP status 404.


Start either profile directly:
# Secure profile, default secure port
python3 lab/web/security_headers_lab.py --profile secure --port 8766

# Baseline profile, default baseline port
python3 lab/web/security_headers_lab.py --profile baseline --port 8765
Inspect both profiles and compare header names and values rather than relying on header ordering:
curl -i http://127.0.0.1:8765/
curl -i http://127.0.0.1:8766/
Use the --help option on a script to view the options supported by that script. If a port is already in use, choose another available port and pass that port consistently to the corresponding assessment command.
Assessment and reports
The assessment module evaluates one explicitly selected STYX-LAB endpoint on 127.0.0.1. It does not scan a network, resolve remote hostnames, or contact an external target.
What is checked
For a valid lab response, the assessment checks:
1. Whether the health and header-metadata endpoints respond.
2. Whether the returned health status and profile are valid.
3. Whether the health profile agrees with the metadata profile.
4. Whether the metadata header map matches the selected profile.
5. Whether each of the five training headers has its expected value, or is absent in the baseline profile.
A complete valid response normally produces nine individual checks. If the service is unavailable or returns invalid JSON, the report records the problem rather than treating the assessment as successful.
Report files
By default, the assessment creates:
File	Contents
reports/latest-assessment.json	Machine-readable assessment metadata and individual check results.
reports/latest-assessment.md	Human-readable summary, scope, observed evidence, and check results.


Choose a separate output directory for a demonstration or to keep runs apart:
python3 -m lab.report --port 8766 --output-dir reports/demo
Interpreting results
Status	Meaning
PASS	The local lab matched the expected behavior for the checks performed.
FAIL	One or more observed values did not match the expectations for the selected profile.
UNAVAILABLE	A required local service response could not be obtained or parsed.


The baseline profile can correctly receive PASS because its documented behavior is to omit the five training headers. Always review the selected profile and the report details; a passing result is evidence about the lab endpoint, not a full audit of an application.
Example of the short terminal summary (illustrative only; real timestamps and results depend on the run):
Assessment result: PASS
JSON report: reports/latest-assessment.json
Markdown report: reports/latest-assessment.md
The JSON report includes the target, profile, overall status, summary totals, and individual checks. Treat reports as potentially sensitive when adapting the lab to include real environment details, and review them before publishing or committing them.
Testing and development
Run the automated tests from the repository root:
python3 -m unittest discover -s tests -v
Run a syntax and bytecode compilation check:
python3 -m compileall -q lab tests
The test suite covers the HTTP profiles and headers, loopback binding, health and metadata endpoints, invalid profile or port values, unknown paths, assessment results, JSON and Markdown report writing, and terminal-interface behavior.
GitHub Actions is configured to run tests and the compile check with Python 3.11, 3.12, and 3.13 on pushes and pull requests. Check the Actions page for the status of the latest workflow run.
When contributing a new scenario, include clear expected behavior, repeatable test steps, evidence to collect, limitations, and cleanup guidance. Add positive and negative tests for behavior that can be tested reliably.
Architecture
The project separates the terminal interface, HTTP lab, and report generation:
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
lab/tui.py	Startup sequence, terminal dashboard, service status display, and interactive menu.
lab/web/security_headers_lab.py	Loopback-only HTTP server, training profiles, and HTTP endpoints.
lab/report.py	Local endpoint assessment and JSON/Markdown report generation.
tests/	Regression tests for the implemented behavior.
.github/workflows/tests.yml	Automated tests and compile checks across supported Python versions.
docs/	Scenario instructions, methodology, and architecture notes.


See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for component boundaries and data flow.
Limitations
STYX-LAB is a focused educational lab for HTTP Security Headers. It is not:
- a general-purpose web application vulnerability scanner;
- a network scanner or packet analyzer;
- a browser-based cross-browser testing framework;
- an authentication system or access-control mechanism;
- a production-ready HTTP server;
- proof of application security or a replacement for a professional security review.
The included service binds to 127.0.0.1 and assessment requests are limited to that loopback host. The exercise uses plain HTTP, and the header set is an illustrative training configuration rather than a universal policy. Header support and behavior vary with browser capabilities and application requirements. Passing the lab checks does not test all application routes, browser behavior, authentication, authorization, dependencies, or business logic.
Responsible use and data handling
Use STYX-LAB for defensive learning and systems you own or are explicitly authorized to examine. The included assessment is restricted to the project's local loopback service; do not expose the training server publicly or adapt the tooling to assess systems without permission.
The lock animation is visual branding, not authentication. Do not treat it as a security control.
For repository vulnerability reporting guidance, see [SECURITY.md](SECURITY.md). Before committing or sharing reports, check them for hostnames, addresses, timestamps, or other environment details that should remain private.
Roadmap ideas
Potential future improvements include:
- another self-contained defensive web-security scenario;
- optional report metadata and improved report presentation;
- better terminal-width handling and accessibility;
- example reports generated from test fixtures.
These are ideas for future work, not features promised in the current version. See [ROADMAP.md](ROADMAP.md) for the maintained project plan.
License
STYX-LAB is released under the MIT License. See LICENSE for the full license text.
