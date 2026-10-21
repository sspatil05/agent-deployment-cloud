"""Connectors are modular: core ships ``http``; everything else (jira, github,
slack, k8s) is an optional extra. Any attribute you import that isn't a real
connector yet comes back as a ``LazyConnector`` so the skeleton stays
importable — calling it tells you exactly what to wire up.
"""
from __future__ import annotations

from .base import Connection, LazyConnector
from .http import HttpConnection

http = HttpConnection()

__all__ = ["Connection", "HttpConnection", "LazyConnector", "http"]


def __getattr__(name: str):
    # jira, slack, github, k8s, ... -> lazy placeholders until implemented
    return LazyConnector(name)
