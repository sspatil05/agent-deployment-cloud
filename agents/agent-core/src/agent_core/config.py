"""Settings — one pydantic ``BaseSettings`` for every agent.

Defaults live in code; overrides come from environment variables (prefixed
``AGENT_``) and, for local development, a ``.env`` file. In-cluster the Helm
chart injects the same env vars (and secrets), so there is nothing extra to
load. Nested keys use ``__`` — e.g. ``AGENT_JIRA__BASE_URL`` -> ``jira["base_url"]``.

``config.py`` inside each agent repo is frozen and just does::

    from agent_core.config import settings
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # identity / behavior
    name: str = "agent"
    model: str | None = None          # LLM model id, or None for no brain
    log_level: str = "INFO"

    # HTTP service
    host: str = "0.0.0.0"
    port: int = 8080

    # per-connector config, filled from env (e.g. AGENT_JIRA__BASE_URL)
    jira: dict = {}
    slack: dict = {}


settings = Settings()
