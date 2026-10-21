"""A keyless provider so a freshly stamped agent runs with no API key.

It never calls tools and returns immediately, so the brain loop exits after one
step. Real reasoning needs a model (AGENT_MODEL) + ANTHROPIC_API_KEY.
"""
from __future__ import annotations

from .base import Reply


class NoOpProvider:
    def __init__(self, model: str | None = None) -> None:
        self.model = model

    def respond(self, system: str, messages: list, tools: list) -> Reply:
        names = ", ".join(t.get("name", "?") for t in tools) or "(none)"
        text = (
            "[no-op brain] No model configured. Set AGENT_MODEL and ANTHROPIC_API_KEY "
            f"to enable reasoning. Available tools: {names}."
        )
        return Reply(content=text, stop_reason="end_turn", text=text)
