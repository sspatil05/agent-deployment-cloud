"""Skills — *markdown* capability docs the LLM reads.

A skill is a ``.md`` file describing a capability in plain language: what the
agent should do and, usually, which tools to use in what order. Skills are
loaded as text and folded into the system prompt; the model follows them and
calls the code Tools (``tools.py``) to actually do the work.

Splitting it this way is deliberate: **skills are declarative (markdown, edited
per agent), tools are executable (code, reusable).**
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    name: str
    content: str


def load_skills(directory: str | Path) -> list[Skill]:
    """Load every ``*.md`` file in ``directory`` as a Skill (sorted by name)."""
    path = Path(directory)
    if not path.exists():
        return []
    return [
        Skill(name=md.stem, content=md.read_text(encoding="utf-8"))
        for md in sorted(path.glob("*.md"))
    ]


def render_skills(skills: list[Skill]) -> str:
    """Concatenate skills into a single markdown block for the system prompt."""
    if not skills:
        return ""
    parts = ["# Skills", "", "Use these capabilities to accomplish the task:"]
    for skill in skills:
        parts.append(f"\n## {skill.name}\n\n{skill.content.strip()}")
    return "\n".join(parts)
