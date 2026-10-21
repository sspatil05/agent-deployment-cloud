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
            return r.status, r.read().decode()

    def test_root_says_hello(self):
        status, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("Hello, World!", body)
        self.assertIn("app1", body)

    def test_health(self):
        self.assertEqual(self.get("/healthz"), (200, "ok\n"))


if __name__ == "__main__":
    unittest.main()
