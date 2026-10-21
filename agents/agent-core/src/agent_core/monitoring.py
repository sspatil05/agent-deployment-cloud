"""Metrics + health — the "line graphs". Minimal stdlib counters here; swap for
a Prometheus client (agent-core[metrics]) when you wire real dashboards."""
from __future__ import annotations


class _Counter:
    def __init__(self) -> None:
        self.value = 0

    def inc(self, n: int = 1) -> None:
        self.value += n


runs_started = _Counter()
runs_ok = _Counter()
runs_failed = _Counter()


def healthz() -> dict:
    return {"status": "ok"}


def metrics() -> dict:
    return {
        "runs_started": runs_started.value,
        "runs_ok": runs_ok.value,
        "runs_failed": runs_failed.value,
    }
