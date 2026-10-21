"""Base class for an agent's custom logic.

Each agent repo defines ``custom/handler.py`` with a ``Handler(BaseHandler)``
that implements ``handle``. This is one of the three files you actually edit.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .context import RunContext


class Handler:
    """Override ``handle`` with the agent's behavior."""

    def handle(self, ctx: RunContext):
        raise NotImplementedError("Define handle() in your custom/handler.py")
