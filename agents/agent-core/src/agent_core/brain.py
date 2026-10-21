"""The brain — an LLM tool-use loop.

Given an agent's prompt + skill docs + tools, and an incoming request, the brain
lets the model call the agent's Tools until it produces a final answer:

    system = prompt + skills(markdown)
    loop:
        reply = model.respond(system, messages, tool_schemas)
        if reply is a final answer -> return it
        otherwise run the requested tools and feed the results back

With no model configured the NoOp provider returns immediately, so this still
runs (does nothing useful) without an API key.
"""
from __future__ import annotations

import json
from typing import Any

from . import monitoring  # noqa: F401  (kept for symmetry; counters live in manager)
from .llm import get_llm
from .logging import get_logger
from .skills import render_skills

log = get_logger("agent.brain")

#: safety cap on tool-use round trips per request
MAX_STEPS = 12


def _system_prompt(agent) -> str:
    parts = [agent.prompt]
    skills_block = render_skills(agent.skills)
    if skills_block:
        parts.append(skills_block)
    return "\n\n".join(parts)


def _stringify(output: Any) -> str:
    if isinstance(output, str):
        return output
    try:
        return json.dumps(output)
    except TypeError:
        return str(output)


def run(agent, payload: dict) -> dict:
    llm = get_llm(agent.model)
    system = _system_prompt(agent)
    tool_schemas = [t.to_schema() for t in agent.tools]
    tool_map = agent.tool_map()

    # The request text the model works from. Convention: {"input": "..."}.
    user_text = payload.get("input") or json.dumps(payload)
    messages: list = [{"role": "user", "content": user_text}]

    for _ in range(MAX_STEPS):
        reply = llm.respond(system=system, messages=messages, tools=tool_schemas)
        messages.append({"role": "assistant", "content": reply.content})

        if reply.stop_reason != "tool_use":
            return {"agent": agent.name, "result": reply.text}

        # Run every requested tool; return one tool_result per call (keyed by id).
        results = []
        for call in reply.tool_calls:
            tool = tool_map.get(call.name)
            try:
                if tool is None:
                    raise KeyError(f"unknown tool: {call.name}")
                output = tool.run(**call.input)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": _stringify(output),
                    }
                )
            except Exception as exc:  # feed the error back so the model can adapt
                log.exception("tool %s failed", call.name)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": str(exc),
                        "is_error": True,
                    }
                )
        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"agent {agent.name} exceeded MAX_STEPS ({MAX_STEPS}) without finishing")
