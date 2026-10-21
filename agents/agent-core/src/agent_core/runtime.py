"""The runtime: every agent is a long-running HTTP service.

``run(agent)`` starts the FastAPI app and blocks. There are no run modes —
triggering (webhooks, schedulers, or other agents) is always an inbound HTTP
call handled by the service.
"""
from __future__ import annotations

from .config import settings
from .logging import configure_logging, get_logger
from .service import serve

log = get_logger("agent.runtime")


def run(agent) -> None:
    configure_logging(settings.log_level)
    log.info("starting agent %s on %s:%s", agent.name, settings.host, settings.port)
    serve(agent, host=settings.host, port=settings.port)
