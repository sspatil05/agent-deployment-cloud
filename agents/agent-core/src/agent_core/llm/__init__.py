"""Factory: pick a provider from the settings and the model id. ``None`` -> keyless NoOp.

Provider selection (``AGENT_LLM_PROVIDER``):
  anthropic   Claude models via the Anthropic API (``ANTHROPIC_API_KEY``)
  openrouter  any model on OpenRouter, e.g. ``openai/gpt-4o-mini`` (``OPENROUTER_API_KEY``)
  auto        (default) a model id containing "/" is an OpenRouter id, anything else is a Claude id
"""
from __future__ import annotations

from ..config import settings
from .base import LLMProvider, Reply, ToolCall
from .noop import NoOpProvider

__all__ = ["LLMProvider", "NoOpProvider", "Reply", "ToolCall", "get_llm"]


def _resolve_provider(model: str) -> str:
    choice = (settings.llm_provider or "auto").lower()
    if choice in ("anthropic", "openrouter"):
        return choice
    return "openrouter" if "/" in model else "anthropic"


def get_llm(model: str | None):
    if not model:
        return NoOpProvider()
    if _resolve_provider(model) == "openrouter":
        from .openrouter import OpenRouterProvider

        return OpenRouterProvider(model=model)
    from .anthropic import AnthropicProvider

    return AnthropicProvider(model=model)
