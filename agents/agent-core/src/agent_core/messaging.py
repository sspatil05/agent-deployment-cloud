"""FUTURE agent-to-agent comms seam. Dormant today.

The interface exists so agents can start talking later without a rewrite.
The default bus is a local no-op; swap for HTTP/queue when comms goes live.
"""
from __future__ import annotations

from typing import Protocol


class AgentBus(Protocol):
    def send(self, to: str, message: dict) -> None: ...


class LocalNoOpBus:
    """Does nothing — a placeholder until inter-agent comms is built."""

    def send(self, to: str, message: dict) -> None:
        return None
