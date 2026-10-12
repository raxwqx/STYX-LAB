"""Local-only HTTP security headers training laboratory.

The service binds exclusively to IPv4 loopback. It is an educational demo,
not a production web server.
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

HOST = "127.0.0.1"
DEFAULT_PORT = 8766
VERSION = "1.0.1"
PROFILES = ("baseline", "secure")

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; object-src 'none'; "
        "base-uri 'self'; frame-ancestors 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "X-Frame-Options": "DENY",
}


class LabHTTPServer(ThreadingHTTPServer):
    """Threaded HTTP server with predictable shutdown behavior."""

    allow_reuse_address = True
    daemon_threads = True


class SecurityHeadersHandler(BaseHTTPRequestHandler):
    """Serve local demonstration endpoints with a selected header profile."""

    profile = "secure"
    server_version = "STYX-LAB/1.0"
    sys_version = ""

    def _send(self, status, content_type, payload):
        body = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if self.profile == "secure":
            for name, value in SECURITY_HEADERS.items():
                self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>STYX-LAB | Security Headers</title>
</head>
<body>
  <main>
    <p><strong>STYHQ // LOCAL SECURITY HQ</strong></p>
    <h1>STYX-LAB: HTTP Security Headers</h1>
    <p>Training profile: <strong>{self.profile}</strong></p>
    <p>This page is served locally for defensive security education.</p>
    <p>Inspect the HTTP response headers and compare the profiles.</p>
    <p>Health endpoint: <code>/health</code></p>
  </main>
</body>
</html>
"""
            self._send(200, "text/html; charset=utf-8", page)
            return

        if path == "/health":
            body = json.dumps({
                "status": "ok",
                "profile": self.profile,
                "version": VERSION,
            }, sort_keys=True)
            self._send(200, "application/json; charset=utf-8", body)
            return

        if path == "/api/headers":
            present = SECURITY_HEADERS if self.profile == "secure" else {}
            body = json.dumps({
                "profile": self.profile,
                "headers": present,
                "version": VERSION,
            }, sort_keys=True)
            self._send(200, "application/json; charset=utf-8", body)
            return

        self._send(
            404,
            "application/json; charset=utf-8",
            json.dumps({"error": "not_found"}, sort_keys=True),
        )

    def do_HEAD(self):
        self.do_GET()

    def log_message(self, format_string, *args):
        """Keep request logs concise and avoid leaking remote network details."""
        super().log_message(format_string, *args)


def create_server(profile="secure", port=DEFAULT_PORT):
    """Create a server bound only to 127.0.0.1.

    Port 0 is accepted for tests to ask the OS for an ephemeral port.
    """
    if profile not in PROFILES:
        raise ValueError("Profile must be 'baseline' or 'secure'.")
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("Port must be an integer between 0 and 65535.")

    handler = type(
        f"{profile.title()}SecurityHeadersHandler",
        (SecurityHeadersHandler,),
        {"profile": profile},
    )
    return LabHTTPServer((HOST, port), handler)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the local-only STYX-LAB HTTP security headers exercise."
    )
    parser.add_argument("--profile", choices=PROFILES, default="secure")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535 when running the CLI.")

    try:
        server = create_server(args.profile, args.port)
    except OSError as exc:
        parser.error(str(exc))

    print(f"STYX-LAB {VERSION} | profile={args.profile}")
    print(f"STYHQ local node: http://{HOST}:{server.server_address[1]}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping STYX-LAB.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
