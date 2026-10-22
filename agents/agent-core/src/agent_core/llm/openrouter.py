"""OpenRouter provider: any model OpenRouter serves (e.g. ``openai/gpt-4o-mini``) behind one OpenAI-style API.

Requires ``agent-core[openrouter]`` (the ``openai`` SDK, pointed at OpenRouter's base URL) and the
``OPENROUTER_API_KEY`` environment variable.

The brain loop speaks Anthropic-shaped messages and tool definitions. This provider translates them to the
OpenAI chat format on the way out and normalizes the reply on the way back, so ``brain.py`` needs no changes.
"""
from __future__ import annotations

import json
import os

from ..logging import get_logger
from .base import Reply, ToolCall

log = get_logger("agent.llm.openrouter")

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
MAX_TOKENS = 4096
#: marks an assistant message that this provider produced, so it can be replayed in OpenAI format
_MARK = "_openai_message"


def _tool_schemas(tools: list) -> list:
    """Anthropic tool definitions -> OpenAI function tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
            },
        }
        for t in tools
    ]


def _messages(system: str, history: list) -> list:
    """Anthropic-shaped history (as kept by the brain loop) -> OpenAI chat messages."""
    out: list = [{"role": "system", "content": system}]
    for msg in history:
        role, content = msg["role"], msg["content"]
        if role == "assistant":
            if isinstance(content, dict) and content.get(_MARK):
                entry = {"role": "assistant", "content": content["content"]}
                if content["tool_calls"]:
                    entry["tool_calls"] = content["tool_calls"]
                out.append(entry)
            else:
                out.append({"role": "assistant", "content": str(content)})
        elif isinstance(content, list):
            # the brain returns tool results as one user message holding several tool_result blocks
            for block in content:
                if block.get("type") == "tool_result":
                    out.append(
                        {
                            "role": "tool",
                            "tool_call_id": block["tool_use_id"],
                            "content": block["content"],
                        }
                    )
        else:
            out.append({"role": "user", "content": content})
    return out


class OpenRouterProvider:
    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        client=None,
    ) -> None:
        self.model = model
        self._api_key = api_key
        self._base_url = base_url or os.environ.get("OPENROUTER_BASE_URL", DEFAULT_BASE_URL)
        self._client = client  # injectable for tests

    def _client_lazy(self):
        if self._client is None:
            from openai import OpenAI  # requires agent-core[openrouter]

            key = self._api_key or os.environ.get("OPENROUTER_API_KEY")
            if not key:
                raise RuntimeError("OPENROUTER_API_KEY is not set")
            self._client = OpenAI(
                api_key=key,
                base_url=self._base_url,
                default_headers={"X-Title": os.environ.get("AGENT_NAME", "agent")},
            )
        return self._client

    def respond(self, system: str, messages: list, tools: list) -> Reply:
        kwargs = {
            "model": self.model,
            "messages": _messages(system, messages),
            "max_tokens": MAX_TOKENS,
        }
        if tools:  # the API rejects an empty tools list
            kwargs["tools"] = _tool_schemas(tools)

        resp = self._client_lazy().chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        raw_calls = list(msg.tool_calls or [])

        tool_calls = []
        for call in raw_calls:
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                log.warning("tool %s returned invalid JSON arguments", call.function.name)
                args = {}
            tool_calls.append(ToolCall(id=call.id, name=call.function.name, input=args))

        content = {
            _MARK: True,
            "content": msg.content,
            "tool_calls": [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {"name": c.function.name, "arguments": c.function.arguments or "{}"},
                }
                for c in raw_calls
            ],
        }
        return Reply(
            content=content,
            stop_reason="tool_use" if tool_calls else "end_turn",
            text=msg.content or "",
            tool_calls=tool_calls,
        )
