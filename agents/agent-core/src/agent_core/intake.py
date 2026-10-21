"""Request acceptance — turn an incoming event/request into a validated payload.

Turns the body of an inbound HTTP request into a validated payload.
"""
from __future__ import annotations

from typing import Any

from .errors import IntakeError


class Intake:
    def accept(self, raw: Any) -> dict:
        """Validate and normalize an incoming request. Extend per transport."""
        if raw is None:
            raise IntakeError("empty request")
        if isinstance(raw, dict):
            return raw
        raise IntakeError(f"unsupported request type: {type(raw).__name__}")
