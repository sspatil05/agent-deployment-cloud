"""Tools for this agent — the code the LLM can call. Edit this file.

Each tool is a small capability with a name, a description (the model reads it to
decide when to call it), a JSON schema for its inputs, and a run() method. List
the tools you want the agent to have in TOOLS at the bottom.
"""
from agent_core import Tool


class Echo(Tool):
    name = "echo"
    description = "Echo the given text back to the caller."
    parameters = {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "text to echo"}},
        "required": ["text"],
    }

    def run(self, text: str):
        return {"echo": text}


# The framework loads this list. Add or remove tools here.
TOOLS = [Echo()]
