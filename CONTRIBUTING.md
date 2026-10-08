# Contributing

Contributions are welcome when they improve the laboratory without turning it into an unnecessarily large framework.

## Guidelines

- Keep scenarios reproducible and isolated.
- Document the expected behavior before adding a test.
- Include remediation guidance for security findings.
- Prefer Python standard library modules where practical.
- Keep commits focused and descriptive.

## Local checks

```bash
python3 -m unittest discover -s tests -v
```
