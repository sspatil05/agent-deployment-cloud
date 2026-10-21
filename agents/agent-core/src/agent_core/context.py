"""RunContext — what a custom Handler receives for a single run.

Only used when an agent supplies its own ``handler`` instead of the default
brain loop. Gives ergonomic access to the agent's tools (``ctx.tools.<name>()``),
the LLM (``ctx.llm``), the request payload, and a ``done()`` helper.
"""
from __future__ import annotations

from typing import Any


class ToolProxy:
    """Lets a handler call tools by name: ``ctx.tools.clone_repo(...)``."""

    def __init__(self, tools: dict[str, Any]):
        self._tools = tools

    def __getattr__(self, name: str):
        try:
            tool = self._tools[name]
        except KeyError as exc:
            raise AttributeError(f"no tool named {name!r}") from exc
        return tool.run


class RunContext:
    def __init__(self, agent, payload: dict | None = None, llm=None):
        self.agent = agent
        self.payload = payload or {}
        self.tools = ToolProxy(agent.tool_map())
        self.llm = llm

    def done(self, result: Any = None) -> dict:
        return {"agent": self.agent.name, "result": result}
