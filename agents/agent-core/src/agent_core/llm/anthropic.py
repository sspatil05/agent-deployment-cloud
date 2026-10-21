"""Default Claude-backed provider — a real Anthropic Messages API tool-use turn.

Requires ``agent-core[anthropic]``. The SDK is imported lazily so ``import
agent_core`` works without it. Each ``respond()`` is one turn of the loop the
brain runs: send system + history + tool schemas, get back either tool calls or
a final answer.
"""
from __future__ import annotations

from .base import Reply, ToolCall

# Default per the Anthropic guidance: use the most capable model unless the
# agent's config pins a different one (settings.model / AGENT_MODEL).
DEFAULT_MODEL = "claude-opus-5"
MAX_TOKENS = 16000


class AnthropicProvider:
    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or DEFAULT_MODEL
        self._api_key = api_key
        self._client = None

    def _client_lazy(self):
        if self._client is None:
            import os

            from anthropic import Anthropic  # requires agent-core[anthropic]

            self._client = Anthropic(
                api_key=self._api_key or os.environ.get("ANTHROPIC_API_KEY")
            )
        return self._client

    def respond(self, system: str, messages: list, tools: list) -> Reply:
        resp = self._client_lazy().messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=system,
            tools=tools,
            messages=messages,
        )
        # tool_use blocks -> ToolCalls the brain will execute; text blocks -> answer.
        tool_calls = [
            ToolCall(id=b.id, name=b.name, input=b.input)
            for b in resp.content
            if b.type == "tool_use"
        ]
        text = "".join(b.text for b in resp.content if b.type == "text")
        # Append resp.content verbatim (preserves tool_use / thinking blocks).
        return Reply(
            content=resp.content,
            stop_reason=resp.stop_reason,
            text=text,
            tool_calls=tool_calls,
        )
