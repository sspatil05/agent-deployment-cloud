"""FUTURE comms shapes. Dormant today — the schemas agents will exchange once
inter-agent communication is turned on. Lives here until comms goes live, then
splits into its own ``agent-contracts`` package that both repos depend on."""
from __future__ import annotations

from pydantic import BaseModel


class AgentMessage(BaseModel):
    sender: str
    recipient: str
    kind: str = "event"
    payload: dict = {}
