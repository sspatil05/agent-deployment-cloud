from agent_core import Tool


class Add(Tool):
    name = "add"
    description = "Add two integers."
    parameters = {
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
    }

    def run(self, a, b):
        return a + b


def test_tool_runs():
    assert Add().run(a=2, b=3) == 5


def test_tool_schema_shape():
    schema = Add().to_schema()
    assert schema["name"] == "add"
    assert schema["input_schema"]["type"] == "object"
    assert "a" in schema["input_schema"]["properties"]
