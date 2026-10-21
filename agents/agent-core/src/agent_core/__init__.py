"""agent_core — the shared framework every agent is built on.

Agents never copy this code; they depend on it as a versioned package
(``agent-core==x.y``). An agent is a prompt + skills (markdown) + tools (code);
the brain runs an LLM tool-use loop over them.
"""
from __future__ import annotations

from . import runtime
from .agent import Agent
from .handler import Handler
from .skills import Skill, load_skills
from .tools import Tool

__version__ = "0.2.0"
__all__ = ["Agent", "Handler", "Skill", "Tool", "__version__", "load_skills", "runtime"]
