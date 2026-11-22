import unittest

from lab.headers import analyze, meets_threshold, summarize
from lab.web.security_headers_lab import SECURITY_HEADERS, WEAK_HEADERS


class HeaderAnalysisTests(unittest.TestCase):
    def test_secure_profile_has_no_findings(self):
        self.assertEqual(analyze(SECURITY_HEADERS), [])

    def test_missing_headers_are_reported(self):
        findings = analyze({})
        reported = {finding["header"] for finding in findings}

        self.assertEqual(reported, set(SECURITY_HEADERS))
        self.assertTrue(
            all(finding["severity"] in ("MEDIUM", "LOW") for finding in findings)
        )

    def test_weak_profile_reports_expected_issues(self):
        findings = analyze(WEAK_HEADERS)
        identifiers = {finding["id"] for finding in findings}

        for identifier in (
            "csp-wildcard",
            "csp-unsafe-inline",
            "csp-unsafe-eval",
            "csp-frame-ancestors",
            "x-content-type-options-value",
            "x-frame-options-value",
            "referrer-policy-unsafe-url",
            "permissions-policy-wildcard",
        ):
            with self.subTest(identifier=identifier):
                self.assertIn(identifier, identifiers)

        self.assertTrue(all(finding["remediation"] for finding in findings))

    def test_empty_values_are_treated_as_missing(self):
        for header in SECURITY_HEADERS:
            with self.subTest(header=header):
                findings = analyze({header: "   "})
                self.assertTrue(
                    any(finding["header"] == header for finding in findings)
                )

    def test_case_insensitive_header_lookup(self):
        headers = {name.lower(): value for name, value in SECURITY_HEADERS.items()}
        self.assertEqual(analyze(headers), [])

    def test_allow_from_is_reported_as_deprecated(self):
        findings = analyze({"X-Frame-Options": "ALLOW-FROM https://example.com"})
        identifiers = {finding["id"] for finding in findings}
        self.assertIn("x-frame-options-deprecated", identifiers)

    def test_severity_summary_counts_every_finding(self):
        findings = analyze(WEAK_HEADERS)
        summary = summarize(findings)

        self.assertEqual(summary["total"], len(findings))
        self.assertEqual(
            summary["total"],
            sum(summary[severity] for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")),
        )

    def test_meets_threshold(self):
        findings = [{"severity": "MEDIUM"}]

        self.assertFalse(meets_threshold([], "low"))
        self.assertFalse(meets_threshold(findings, "none"))
        self.assertFalse(meets_threshold(findings, "high"))
        self.assertTrue(meets_threshold(findings, "medium"))
        self.assertTrue(meets_threshold(findings, "low"))

    def test_unknown_threshold_is_rejected(self):
        with self.assertRaises(ValueError):
            meets_threshold([{"severity": "LOW"}], "severe")


if __name__ == "__main__":
    unittest.main()
