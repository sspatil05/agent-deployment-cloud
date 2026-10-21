"""The smallest agent you can write against the framework.

A prompt + one tool. With no model set it runs the keyless NoOp brain; set
AGENT_MODEL + ANTHROPIC_API_KEY to have the LLM actually call the tool.
"""
from agent_core import Agent, Tool, runtime


class Hello(Tool):
    name = "hello"
    description = "Say hello to someone."
    parameters = {"type": "object", "properties": {"who": {"type": "string"}}}

    def run(self, who: str = "world"):
        return f"hello, {who}"


agent = Agent(
    name="minimal",
    prompt="Greet the user by name using the hello tool.",
    tools=[Hello()],
    model=None,  # set to e.g. "claude-opus-5" to enable the LLM brain
)

if __name__ == "__main__":
    runtime.run(agent)
