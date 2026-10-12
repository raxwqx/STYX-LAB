# Contributing

Contributions should improve correctness, reproducibility, accessibility,
test coverage, or defensive learning value.

## Guidelines

- Keep experiments local, scoped, and reproducible.
- Document expected behavior before writing validation checks.
- Include remediation, evidence, limitations, and cleanup instructions.
- Prefer the Python standard library when practical.
- Do not add real credentials, personal data, or external targets.
- Keep commits focused and describe what was changed.

## Local validation

Use Python 3.11 or newer:

    python3 -m unittest discover -s tests -v
    python3 -m py_compile lab/tui.py lab/report.py lab/web/security_headers_lab.py

A test passing is evidence only for the behavior covered by that test.
