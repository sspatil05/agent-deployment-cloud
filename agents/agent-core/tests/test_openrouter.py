"""OpenRouter provider tests. A fake client stands in for the network, so these cost nothing."""
import json
from types import SimpleNamespace

import pytest

from agent_core import Agent, Tool, brain
from agent_core.llm import get_llm
from agent_core.llm.noop import NoOpProvider
from agent_core.llm.openrouter import OpenRouterProvider


class Echo(Tool):
    name = "echo"
    description = "Echo the text back."
    parameters = {"type": "object", "properties": {"text": {"type": "string"}}}

    def run(self, text=""):
        return {"echo": text}


def _reply(content=None, tool_calls=None):
    msg = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def _call(call_id, name, args):
    return SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=json.dumps(args)))


class FakeClient:
    """Returns queued replies and records every request it receives."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        return self.replies.pop(0)


def test_provider_selection(monkeypatch):
    from agent_core.config import settings

    monkeypatch.setattr(settings, "llm_provider", "auto")
    assert isinstance(get_llm(None), NoOpProvider)
    assert isinstance(get_llm("openai/gpt-4o-mini"), OpenRouterProvider)
    pytest.importorskip("anthropic")
    assert type(get_llm("claude-sonnet-5-5")).__name__ == "AnthropicProvider"
    monkeypatch.setattr(settings, "llm_provider", "openrouter")
    assert isinstance(get_llm("anything"), OpenRouterProvider)


def test_plain_answer():
    client = FakeClient([_reply(content="hi there")])
    provider = OpenRouterProvider("openai/gpt-4o-mini", client=client)
    reply = provider.respond("be nice", [{"role": "user", "content": "hello"}], [])
    assert reply.text == "hi there"
    assert reply.stop_reason == "end_turn"
    sent = client.requests[0]
    assert sent["model"] == "openai/gpt-4o-mini"
    assert sent["messages"][0] == {"role": "system", "content": "be nice"}
    assert "tools" not in sent  # an empty tools list would be rejected by the API


def test_full_tool_loop_through_the_brain(monkeypatch):
    client = FakeClient(
        [
            _reply(tool_calls=[_call("call_1", "echo", {"text": "ping"})]),
            _reply(content="the tool said ping"),
        ]
    )
    monkeypatch.setattr(
        "agent_core.brain.get_llm", lambda model: OpenRouterProvider(model, client=client)
    )
    agent = Agent(name="t", prompt="use tools", tools=[Echo()], model="openai/gpt-4o-mini")

    out = brain.run(agent, {"input": "echo ping"})

    assert out == {"agent": "t", "result": "the tool said ping"}
    first, second = client.requests
    assert first["tools"][0]["function"]["name"] == "echo"
    # second request replays the assistant tool call and the tool result in OpenAI format
    roles = [m["role"] for m in second["messages"]]
    assert roles == ["system", "user", "assistant", "tool"]
    assert second["messages"][2]["tool_calls"][0]["id"] == "call_1"
    assert second["messages"][3]["tool_call_id"] == "call_1"
    assert json.loads(second["messages"][3]["content"]) == {"echo": "ping"}


def test_invalid_tool_arguments_do_not_crash():
    bad = SimpleNamespace(id="c", function=SimpleNamespace(name="echo", arguments="{not json"))
    client = FakeClient([_reply(tool_calls=[bad])])
    provider = OpenRouterProvider("openai/gpt-4o-mini", client=client)
    reply = provider.respond("s", [{"role": "user", "content": "x"}], [Echo().to_schema()])
    assert reply.tool_calls[0].input == {}


def test_missing_key_gives_a_clear_error(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    pytest.importorskip("openai")
    provider = OpenRouterProvider("openai/gpt-4o-mini")
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        provider.respond("s", [{"role": "user", "content": "x"}], [])
