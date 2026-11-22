"""Header quality analysis for the local STYX-LAB assessment.

The lab server reports which headers it sends. Presence alone is not enough:
a header can be present and still be weak. This module turns observed header
values into deterministic, severity-ranked findings with remediation notes.

It is pure: it performs no network requests and knows nothing about profiles.
"""

from __future__ import annotations

SEVERITY_ORDER = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
SEVERITY_RANK = {severity: index for index, severity in enumerate(SEVERITY_ORDER)}

CSP_HEADER = "Content-Security-Policy"

KNOWN_REFERRER_POLICIES = {
    "no-referrer",
    "no-referrer-when-downgrade",
    "origin",
    "origin-when-cross-origin",
    "same-origin",
    "strict-origin",
    "strict-origin-when-cross-origin",
    "unsafe-url",
}


def _lookup(headers, name):
    """Return a header value using a case-insensitive lookup."""
    if not headers:
        return None

    getter = getattr(headers, "get", None)
    if getter is not None:
        try:
            value = getter(name)
        except TypeError:
            value = None
        if value is not None:
            return value

    try:
        items = headers.items()
    except AttributeError:
        return None

    for key, value in items:
        if str(key).lower() == name.lower():
            return value
    return None


def _value(headers, name):
    """Return a trimmed string value, or ``None`` when absent or empty."""
    raw = _lookup(headers, name)
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _finding(identifier, severity, header, message, remediation):
    return {
        "id": identifier,
        "severity": severity,
        "header": header,
        "message": message,
        "remediation": remediation,
    }


def _csp_directives(value):
    """Parse a CSP string into ``{directive: [tokens]}`` (lower-cased)."""
    directives = {}
    for part in str(value).split(";"):
        tokens = part.split()
        if not tokens:
            continue
        directives[tokens[0].lower()] = [token.lower() for token in tokens[1:]]
    return directives


def _csp_findings(value):
    findings = []
    directives = _csp_directives(value)

    wildcard_directives = sorted(
        name
        for name in ("default-src", "script-src", "style-src", "object-src")
        if "*" in directives.get(name, [])
    )
    if wildcard_directives:
        findings.append(
            _finding(
                "csp-wildcard",
                "HIGH",
                CSP_HEADER,
                "CSP allows every source (*) in " + ", ".join(wildcard_directives),
                "Replace wildcard sources with explicit, minimal origins.",
            )
        )

    script_like = directives.get("default-src", []) + directives.get("script-src", [])
    style_like = directives.get("default-src", []) + directives.get("style-src", [])

    if "'unsafe-inline'" in script_like or "'unsafe-inline'" in style_like:
        findings.append(
            _finding(
                "csp-unsafe-inline",
                "MEDIUM",
                CSP_HEADER,
                "CSP permits 'unsafe-inline' scripts or styles",
                "Use nonces or hashes instead of 'unsafe-inline'.",
            )
        )

    if "'unsafe-eval'" in script_like:
        findings.append(
            _finding(
                "csp-unsafe-eval",
                "MEDIUM",
                CSP_HEADER,
                "CSP permits 'unsafe-eval'",
                "Remove 'unsafe-eval' and refactor code that relies on dynamic evaluation.",
            )
        )

    if "frame-ancestors" not in directives:
        findings.append(
            _finding(
                "csp-frame-ancestors",
                "LOW",
                CSP_HEADER,
                "CSP has no frame-ancestors directive",
                "Add frame-ancestors 'none' or an explicit list of trusted parents.",
            )
        )

    if "object-src" not in directives and "default-src" not in directives:
        findings.append(
            _finding(
                "csp-object-src",
                "LOW",
                CSP_HEADER,
                "CSP restricts neither object-src nor default-src",
                "Add object-src 'none' or a restrictive default-src.",
            )
        )

    return findings


def analyze(headers):
    """Return severity-ranked findings for the five training headers."""
    findings = []

    # ---------------------------------------------------------------
    # Content-Security-Policy
    # ---------------------------------------------------------------
    csp = _value(headers, CSP_HEADER)
    if csp is None:
        findings.append(
            _finding(
                "csp-missing",
                "MEDIUM",
                CSP_HEADER,
                "Content-Security-Policy is missing",
                "Define a restrictive Content-Security-Policy for the application.",
            )
        )
    else:
        findings.extend(_csp_findings(csp))

    # ---------------------------------------------------------------
    # X-Content-Type-Options
    # ---------------------------------------------------------------
    content_type_options = _value(headers, "X-Content-Type-Options")
    if content_type_options is None:
        findings.append(
            _finding(
                "x-content-type-options-missing",
                "LOW",
                "X-Content-Type-Options",
                "X-Content-Type-Options is missing",
                "Send X-Content-Type-Options: nosniff.",
            )
        )
    elif content_type_options.lower() != "nosniff":
        findings.append(
            _finding(
                "x-content-type-options-value",
                "LOW",
                "X-Content-Type-Options",
                f"X-Content-Type-Options is {content_type_options!r}, not 'nosniff'",
                "Set X-Content-Type-Options to exactly nosniff.",
            )
        )

    # ---------------------------------------------------------------
    # X-Frame-Options
    # ---------------------------------------------------------------
    frame_options = _value(headers, "X-Frame-Options")
    if frame_options is None:
        findings.append(
            _finding(
                "x-frame-options-missing",
                "LOW",
                "X-Frame-Options",
                "X-Frame-Options is missing",
                "Send X-Frame-Options: DENY or SAMEORIGIN, or enforce frame-ancestors in CSP.",
            )
        )
    else:
        normalized = frame_options.lower()
        if normalized not in ("deny", "sameorigin"):
            if normalized.startswith("allow-from"):
                findings.append(
                    _finding(
                        "x-frame-options-deprecated",
                        "INFO",
                        "X-Frame-Options",
                        "X-Frame-Options uses the obsolete ALLOW-FROM form",
                        "Use CSP frame-ancestors instead of ALLOW-FROM.",
                    )
                )
            else:
                findings.append(
                    _finding(
                        "x-frame-options-value",
                        "MEDIUM",
                        "X-Frame-Options",
                        f"X-Frame-Options has an invalid value: {frame_options!r}",
                        "Use DENY or SAMEORIGIN; invalid values are ignored by browsers.",
                    )
                )

    # ---------------------------------------------------------------
    # Referrer-Policy
    # ---------------------------------------------------------------
    referrer_policy = _value(headers, "Referrer-Policy")
    if referrer_policy is None:
        findings.append(
            _finding(
                "referrer-policy-missing",
                "LOW",
                "Referrer-Policy",
                "Referrer-Policy is missing",
                "Send Referrer-Policy: strict-origin-when-cross-origin or stricter.",
            )
        )
    else:
        policies = [
            token.strip().lower()
            for token in referrer_policy.split(",")
            if token.strip()
        ]
        if "unsafe-url" in policies:
            findings.append(
                _finding(
                    "referrer-policy-unsafe-url",
                    "MEDIUM",
                    "Referrer-Policy",
                    "Referrer-Policy uses unsafe-url and leaks full URLs",
                    "Use strict-origin-when-cross-origin, same-origin, or no-referrer.",
                )
            )
        elif "no-referrer-when-downgrade" in policies:
            findings.append(
                _finding(
                    "referrer-policy-weak",
                    "LOW",
                    "Referrer-Policy",
                    "Referrer-Policy uses the legacy no-referrer-when-downgrade value",
                    "Prefer strict-origin-when-cross-origin or a stricter policy.",
                )
            )
        elif not any(policy in KNOWN_REFERRER_POLICIES for policy in policies):
            findings.append(
                _finding(
                    "referrer-policy-unrecognized",
                    "LOW",
                    "Referrer-Policy",
                    f"Referrer-Policy has an unrecognized value: {referrer_policy!r}",
                    "Use a standard Referrer-Policy value.",
                )
            )

    # ---------------------------------------------------------------
    # Permissions-Policy
    # ---------------------------------------------------------------
    permissions_policy = _value(headers, "Permissions-Policy")
    if permissions_policy is None:
        findings.append(
            _finding(
                "permissions-policy-missing",
                "LOW",
                "Permissions-Policy",
                "Permissions-Policy is missing",
                "Disable unused browser features explicitly, for example camera=(), microphone=().",
            )
        )
    elif "*" in permissions_policy:
        findings.append(
            _finding(
                "permissions-policy-wildcard",
                "MEDIUM",
                "Permissions-Policy",
                "Permissions-Policy grants features to every origin (*)",
                "Replace wildcard allowlists with explicit origins or empty allowlists.",
            )
        )

    return findings


def summarize(findings):
    """Count findings by severity, with a ``total`` key."""
    summary = {severity: 0 for severity in SEVERITY_ORDER}

    for finding in findings or []:
        severity = str(finding.get("severity", "INFO")).upper()
        if severity not in summary:
            severity = "INFO"
        summary[severity] += 1

    summary["total"] = len(findings or [])
    return summary


def meets_threshold(findings, threshold):
    """Return ``True`` when any finding is at least as severe as *threshold*."""
    threshold = str(threshold).lower()
    if threshold == "none":
        return False

    limit = SEVERITY_RANK.get(threshold.upper())
    if limit is None:
        raise ValueError(f"Unknown severity threshold: {threshold}")

    for finding in findings or []:
        severity = str(finding.get("severity", "INFO")).upper()
        if SEVERITY_RANK.get(severity, SEVERITY_RANK["INFO"]) <= limit:
            return True
    return False
