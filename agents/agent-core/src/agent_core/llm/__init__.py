"""Factory: pick a provider from a model id. ``None`` -> keyless NoOp."""
from __future__ import annotations

from .base import LLMProvider, Reply, ToolCall
from .noop import NoOpProvider

__all__ = ["LLMProvider", "NoOpProvider", "Reply", "ToolCall", "get_llm"]


def get_llm(model: str | None):
    if not model:
        return NoOpProvider()
    # Everything is Anthropic/Claude by default; add branches for other providers.
    from .anthropic import AnthropicProvider

    return AnthropicProvider(model=model)
