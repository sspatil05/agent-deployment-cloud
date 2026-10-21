"""The Agent object — the single assembly point every agent repo wires up.

An agent is: a **prompt** (its role), a set of **skills** (markdown docs the LLM
reads), a set of **tools** (code the LLM can call), an optional **model**, and
an optional **handler** for custom orchestration. With no handler, the brain
(``brain.py``) drives an LLM tool-use loop; with a handler, your code drives.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .handler import Handler
    from .skills import Skill
    from .tools import Tool


@dataclass
class Agent:
    name: str
    prompt: str
    skills: list[Skill] = field(default_factory=list)   # markdown docs
    tools: list[Tool] = field(default_factory=list)      # code capabilities
    handler: Handler | None = None                        # optional custom orchestration
    model: str | None = None                                # LLM model id, or None for the no-op brain
    console_html: str | None = None                         # custom HTML for GET / (overrides the default console)

    def tool_map(self) -> dict[str, Tool]:
        return {t.name: t for t in self.tools}
