"""app2: a tiny JSON hello world web service (standard library only)."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

APP_NAME = os.getenv("APP_NAME", "app2")
APP_VERSION = os.getenv("APP_VERSION", "dev")
ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "local")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, {"status": "ok"})
        else:
            self._send(
                200,
                {
                    "app": APP_NAME,
                    "message": "Hello, World!",
                    "version": APP_VERSION,
                    "environment": ENVIRONMENT,
                },
            )

    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # keep container logs to one line per request
        print(f"{self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
