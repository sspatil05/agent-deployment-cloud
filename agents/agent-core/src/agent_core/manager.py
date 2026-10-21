"""RunManager — orchestrates a single request.

Default path: the brain loop (LLM + tools). If the agent supplies a custom
``handler``, that runs instead. Either way, one JSON result comes back and the
run counters are updated.
"""
from __future__ import annotations

from . import brain, monitoring
from .context import RunContext
from .llm import get_llm
from .logging import get_logger

log = get_logger("agent.manager")


class RunManager:
    def __init__(self, agent) -> None:
        self.agent = agent

    def run_once(self, payload: dict | None = None):
        payload = payload or {}
        monitoring.runs_started.inc()
        try:
            if self.agent.handler is not None:
                ctx = RunContext(self.agent, payload=payload, llm=get_llm(self.agent.model))
                result = self.agent.handler.handle(ctx)
            else:
                result = brain.run(self.agent, payload)
            monitoring.runs_ok.inc()
            log.info("run complete: %s", self.agent.name)
            return result
        except Exception:
            monitoring.runs_failed.inc()
            log.exception("run failed: %s", self.agent.name)
            raise
