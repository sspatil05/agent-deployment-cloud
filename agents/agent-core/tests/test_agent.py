from agent_core import Agent, Skill, Tool
from agent_core.manager import RunManager
from agent_core.skills import render_skills


class Echo(Tool):
    name = "echo"
    description = "Echo the text back."
    parameters = {"type": "object", "properties": {"text": {"type": "string"}}}

    def run(self, text=""):
        return {"echo": text}


def test_agent_runs_with_noop_brain():
    # No model -> NoOp brain -> returns a result dict without calling any API.
    agent = Agent(name="t", prompt="hi", tools=[Echo()])
    out = RunManager(agent).run_once({"input": "hello"})
    assert out["agent"] == "t"
    assert "result" in out


def test_render_skills_includes_content():
    block = render_skills([Skill(name="greet", content="Say hello politely.")])
    assert "greet" in block
    assert "Say hello politely." in block
