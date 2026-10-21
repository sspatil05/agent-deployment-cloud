"""LLMProvider — the pluggable brain interface, plus the normalized reply shape
the brain loop consumes (so Anthropic and the keyless NoOp look identical to it)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class Reply:
    #: assistant content to append to the message history (raw blocks for Anthropic)
    content: Any
    #: "tool_use" means the model wants to call tools; anything else ends the loop
    stop_reason: str
    #: the final text answer (when not calling tools)
    text: str = ""
    #: the tool calls the model requested this turn
    tool_calls: list[ToolCall] = field(default_factory=list)


@runtime_checkable
class LLMProvider(Protocol):
    def respond(self, system: str, messages: list, tools: list) -> Reply: ...
