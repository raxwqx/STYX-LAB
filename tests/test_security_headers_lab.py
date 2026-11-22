import json
import threading
import unittest
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.request import urlopen

from lab.web.security_headers_lab import (
    HOST,
    PROFILES,
    SECURITY_HEADERS,
    VERSION,
    WEAK_HEADERS,
    create_server,
)


@contextmanager
def running_server(profile):
    server = create_server(profile=profile, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://{HOST}:{server.server_address[1]}"
    try:
        yield base
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


class SecurityHeadersLabTests(unittest.TestCase):
    def test_server_binds_to_loopback(self):
        server = create_server("secure", 0)
        try:
            self.assertEqual(server.server_address[0], HOST)
        finally:
            server.server_close()

    def test_profiles_include_secure_baseline_and_weak(self):
        self.assertEqual(PROFILES, ("baseline", "secure", "weak"))

    def test_secure_profile_sets_all_security_headers(self):
        with running_server("secure") as base:
            with urlopen(base + "/", timeout=3) as response:
                self.assertEqual(response.status, 200)
                for name, expected in SECURITY_HEADERS.items():
                    with self.subTest(header=name):
                        self.assertEqual(response.headers.get(name), expected)

    def test_server_header_has_no_trailing_space_and_tracks_version(self):
        with running_server("secure") as base:
            with urlopen(base + "/", timeout=3) as response:
                self.assertEqual(response.headers.get("Server"), f"STYX-LAB/{VERSION}")

    def test_baseline_omits_security_headers(self):
        with running_server("baseline") as base:
            with urlopen(base + "/", timeout=3) as response:
                self.assertEqual(response.status, 200)
                for name in SECURITY_HEADERS:
                    with self.subTest(header=name):
                        self.assertIsNone(response.headers.get(name))

    def test_weak_profile_sends_weak_but_present_headers(self):
        with running_server("weak") as base:
            with urlopen(base + "/", timeout=3) as response:
                self.assertEqual(response.status, 200)
                for name, expected in WEAK_HEADERS.items():
                    with self.subTest(header=name):
                        self.assertEqual(response.headers.get(name), expected)

    def test_health_endpoint_reports_profile_and_version(self):
        for profile in PROFILES:
            with self.subTest(profile=profile), running_server(profile) as base:
                with urlopen(base + "/health", timeout=3) as response:
                    payload = json.load(response)
                    self.assertEqual(response.status, 200)
                    self.assertEqual(payload["status"], "ok")
                    self.assertEqual(payload["profile"], profile)
                    self.assertEqual(payload["version"], VERSION)

    def test_headers_metadata_endpoint(self):
        expected = {
            "baseline": {},
            "secure": SECURITY_HEADERS,
            "weak": WEAK_HEADERS,
        }
        for profile, headers in expected.items():
            with self.subTest(profile=profile), running_server(profile) as base:
                with urlopen(base + "/api/headers", timeout=3) as response:
                    payload = json.load(response)
                    self.assertEqual(payload["profile"], profile)
                    self.assertEqual(payload["headers"], headers)

    def test_unknown_path_returns_json_404(self):
        with running_server("secure") as base:
            with self.assertRaises(HTTPError) as caught:
                urlopen(base + "/not-found", timeout=3)
            error = caught.exception
            try:
                self.assertEqual(error.code, 404)
                self.assertEqual(json.loads(error.read()), {"error": "not_found"})
            finally:
                error.close()

    def test_invalid_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            create_server("invalid", 0)

    def test_invalid_ports_are_rejected(self):
        for port in (-1, 65536, "8765", True):
            with self.subTest(port=port), self.assertRaises(ValueError):
                create_server("secure", port)


if __name__ == "__main__":
    unittest.main()
