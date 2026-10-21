import json
import threading
import unittest
import urllib.request
from http.server import HTTPServer

import app


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}") as r:
            return r.status, json.loads(r.read().decode())

    def test_root_says_hello(self):
        status, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertEqual(body["message"], "Hello, World!")
        self.assertEqual(body["app"], "app2")

    def test_health(self):
        self.assertEqual(self.get("/healthz"), (200, {"status": "ok"}))


if __name__ == "__main__":
    unittest.main()
