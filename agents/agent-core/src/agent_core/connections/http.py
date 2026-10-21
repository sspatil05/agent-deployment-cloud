"""A generic HTTP connector — the one connector that ships in core."""
from __future__ import annotations

from .base import Connection


class HttpConnection(Connection):
    name = "http"

    def __init__(self, base_url: str = "") -> None:
        self.base_url = base_url

    def get(self, path: str, **kwargs):
        raise NotImplementedError("wire up httpx/requests in implementation")

    def post(self, path: str, **kwargs):
        raise NotImplementedError("wire up httpx/requests in implementation")
