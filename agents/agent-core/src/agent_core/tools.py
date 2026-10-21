"""Tools — the *code* capabilities the LLM can call.

In this framework a **tool** is executable code (clone a repo, call an API,
render a template); a **skill** is a markdown doc that tells the LLM how to use
the tools (see ``skills.py``). The brain (``brain.py``) gives the model the
tool schemas and runs whichever tools it decides to call.

A Tool wraps a callable with three things the model needs: a ``name``, a
``description``, and a JSON-schema for its inputs. ``to_schema()`` renders the
exact shape the Anthropic Messages API expects in its ``tools`` list.
"""
from __future__ import annotations

from typing import Any


class Tool:
    #: unique name the model calls the tool by
    name: str = ""
    #: what the tool does + when to use it (the model reads this)
    description: str = ""
    #: JSON schema for the tool's inputs
    parameters: dict = {"type": "object", "properties": {}}

    def run(self, **kwargs: Any) -> Any:
        """Execute the tool. Override in a subclass."""
        raise NotImplementedError("Implement run() in your Tool subclass")

    def to_schema(self) -> dict:
        """Render the Anthropic tool-definition shape."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }
