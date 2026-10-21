"""Connection interface + a lazy placeholder so ``from agent_core.connections
import jira`` works even before that connector is implemented/installed."""
from __future__ import annotations

from typing import Any


class Connection:
    """Base for a connector (Jira, GitHub, Slack, k8s, ...)."""

    name: str = ""


class LazyConnector:
    """Returned for any not-yet-implemented connector. Importing it is fine;
    calling it tells you exactly what to wire up."""

    def __init__(self, name: str) -> None:
        self._name = name

    def __getattr__(self, attr: str):
        def _stub(*args: Any, **kwargs: Any):
            raise NotImplementedError(
                f"connector '{self._name}.{attr}' is a skeleton — implement it "
                f"(install agent-core[{self._name}] and wire the client)"
            )

        return _stub
