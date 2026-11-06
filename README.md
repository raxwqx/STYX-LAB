
# 🧪 STYX-LAB

<p align="center">
  <strong>Local-first Cybersecurity Research & Training Laboratory</strong><br>
  Learn. Analyze. Verify. Document.
</p>

<p align="center">
  <a href="README.md">🇬🇧 English</a> · <a href="README_TR.md">🇹🇷 Türkçe</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-14243A?style=for-the-badge&logo=python&logoColor=F2E8D5" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Platform-Linux-14243A?style=for-the-badge&logo=linux&logoColor=F2E8D5" alt="Linux">
  <img src="https://img.shields.io/badge/License-MIT-14243A?style=for-the-badge&logo=opensourceinitiative&logoColor=F2E8D5" alt="MIT License">
  <img src="https://img.shields.io/badge/Runtime%20Dependencies-None-14243A?style=for-the-badge&logo=python&logoColor=F2E8D5" alt="No runtime dependencies">
</p>

<p align="center">
  <a href="https://github.com/raxwqx/STYX-LAB/actions/workflows/tests.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/raxwqx/STYX-LAB/tests.yml?branch=main&style=for-the-badge&label=Python%20CI&color=14243A&logo=githubactions&logoColor=F2E8D5" alt="Python CI">
  </a>
</p>

---

## ◈ About

**STYX-LAB** is an open-source cybersecurity research and training laboratory focused on practical, reproducible, and responsible security learning.

The current implementation provides a local HTTP Security Headers environment built with Python. It lets learners compare two server configurations, inspect HTTP responses, perform local assessments, and generate structured evidence reports.

> Understand the behavior. Verify the evidence. Document the result.

## ✦ Project Highlights

| Component | Description |
|:--|:--|
| 🖥️ Terminal Control Deck | Interactive terminal interface |
| 🌐 HTTP Security Lab | Local HTTP server with two profiles |
| 🔐 Security Headers | Demonstrates five HTTP response headers |
| 📊 Assessment Engine | Local configuration and response checks |
| 📁 Evidence Reports | JSON and Markdown report generation |
| 🧪 Automated Testing | Unit and integration tests |
| ⚙️ GitHub Actions | Automated CI checks |

## 🔬 Current Research Scenario: HTTP Security Headers

STYX-LAB currently includes two comparison profiles:

| Profile | Description |
|:--|:--|
| `secure` | Sends the configured training security headers |
| `baseline` | Deliberately omits the five demonstrated headers |

Headers demonstrated:

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `X-Frame-Options`

Both profiles use `Cache-Control: no-store`. The `baseline` profile is for comparison only, not production use.

### Assessment workflow

```text
       Select a lab profile
               |
               v
       Start local HTTP service
               |
               v
       Inspect HTTP responses
               |
               v
       Run local assessment
               |
               v
       Compare expected values
               |
               v
          Record evidence
               |
          _____|_____
         |           |
         v           v
     JSON report  Markdown report
```

**Analyst note:** A passing assessment confirms only that the local lab behaved as expected for the checks performed. It does not prove that a real application is secure.

## ⚡ Quick Start

### Requirements

- Python 3.11 or newer
- Linux or another supported Python environment
- Terminal access
- `curl` (optional)

No third-party Python runtime dependencies are required.

### 1. Clone the repository

```bash
git clone https://github.com/raxwqx/STYX-LAB.git
cd STYX-LAB
```

### 2. Launch the terminal control deck

```bash
python3 lab/tui.py
```

### 3. Start the secure profile directly

```bash
python3 lab/web/security_headers_lab.py --profile secure --port 8766
```

### 4. Inspect the local service

```bash
curl -i http://127.0.0.1:8766/
curl -i http://127.0.0.1:8766/health
curl -i http://127.0.0.1:8766/api/headers
```

### 5. Generate an assessment report

```bash
python3 -m lab.report --port 8766
```

Default report files:

```text
reports/
├── latest-assessment.json
└── latest-assessment.md
```

Stop the server with `Ctrl+C` when finished.

## 🧭 Control Deck

Run `python3 lab/tui.py` from the repository root.

| Key | Action |
|:--:|:--|
| `1` | Launch secure profile |
| `2` | Launch baseline profile |
| `3` | Run automated tests |
| `4` | Run local assessment |
| `5` | Read scenario guide |
| `0` | Exit |

Default ports: secure `8766`, baseline `8765`.

Optional settings:

```bash
STYXLAB_NO_ANIMATION=1 python3 lab/tui.py
NO_COLOR=1 python3 lab/tui.py
```

The startup lock animation is visual branding only. It is not authentication or access control.

## 📡 Endpoints

| Endpoint | Method | Purpose |
|:--|:--:|:--|
| `/` | GET | Training homepage |
| `/health` | GET | JSON service status |
| `/api/headers` | GET | Active profile and header metadata |
| Unknown path | GET | JSON 404 response |

The included service binds to `127.0.0.1`.

## 📑 Assessment & Reports

The assessment tool checks:

1. Local service availability.
2. Health endpoint response.
3. Profile consistency between endpoints.
4. Header metadata.
5. Expected values or absence of the five training headers.

A complete valid response normally produces nine individual checks.

| Status | Meaning |
|:--|:--|
| `PASS` | Expected local behavior observed |
| `FAIL` | One or more checks did not match |
| `UNAVAILABLE` | Required local response could not be obtained or parsed |

Generate reports in a separate directory:

```bash
python3 -m lab.report --port 8766 --output-dir reports/demo
```

Review reports before publishing them. They may contain environment information that should remain private.

## 🧪 Testing

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q lab tests
```

GitHub Actions runs automated checks with Python 3.11, 3.12, and 3.13.

[View GitHub Actions](https://github.com/raxwqx/STYX-LAB/actions)

## 🏗️ Project Structure

```text
STYX-LAB/
├── .github/workflows/tests.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── methodology/
│   └── scenarios/
├── lab/
│   ├── __init__.py
│   ├── report.py
│   ├── tui.py
│   └── web/
│       ├── __init__.py
│       └── security_headers_lab.py
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
├── README_TR.md
├── ROADMAP.md
└── SECURITY.md
```

## 🛡️ Scope & Responsible Use

STYX-LAB is an educational and defensive security project. The current implementation:

- Uses a local HTTP service bound to `127.0.0.1`.
- Assesses only the local STYX-LAB service.
- Does not scan external hosts or networks.
- Does not resolve remote hostnames.
- Is not a general-purpose vulnerability scanner.
- Is not intended for public production deployment.

Use security tools only on systems you own or have explicit permission to assess. See [SECURITY.md](SECURITY.md).

## 🗺️ Roadmap

Potential future improvements include additional self-contained defensive scenarios, improved report metadata and presentation, better terminal accessibility, and example reports from test fixtures.

These are future ideas, not features currently included. See [ROADMAP.md](ROADMAP.md).

---

## 🔭 Project Vision

STYX-LAB is designed to grow beyond its current HTTP Security Headers training environment into a modular cybersecurity research platform.

The long-term vision includes three main areas:

### 🕵️ OSINT (Open-Source Intelligence)
Tools and workflows for collecting, organizing, correlating, and analyzing publicly available information.

### 🔬 Digital Forensics
Capabilities for examining digital evidence, preserving file integrity, analyzing metadata, building timelines, and documenting findings.

### 🛡️ Cybersecurity Laboratory
A collection of isolated, educational environments and practical tools for learning, testing, and understanding cybersecurity concepts.

### Our Goal

To bring OSINT, digital forensics, and cybersecurity research together under one modular platform, with an emphasis on transparency, reproducibility, responsible research, and open-source development.

**Development note:** These are long-term project goals. The current implementation focuses on HTTP Security Headers training and assessment. Future capabilities will be introduced gradually and documented as they become available.

## 🤝 Contributing

Contributions are welcome.

1. Read [CONTRIBUTING.md](CONTRIBUTING.md).
2. Keep experiments local, scoped, and reproducible.
3. Include tests for new behavior.
4. Never commit credentials or private information.

## 📜 License

STYX-LAB is released under the [MIT License](LICENSE).

---

<p align="center">
  <strong>STYX-LAB</strong><br>
  <sub>Research responsibly. Investigate carefully. Build openly.</sub><br><br>
  <a href="https://github.com/raxwqx/STYX-LAB">GitHub Repository</a> ·
  <a href="https://github.com/raxwqx">Developer Profile</a>
</p>
