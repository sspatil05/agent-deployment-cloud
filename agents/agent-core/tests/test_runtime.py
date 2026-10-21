from agent_core import Agent
from agent_core.service import RunRequest, create_app


def test_service_exposes_health_routes():
    app = create_app(Agent(name="t", prompt="x"))
    paths = {route.path for route in app.routes}
    assert "/healthz" in paths
    assert "/readyz" in paths
    assert "/run" in paths


def test_run_request_accepts_structured_input():
    """Regression: ``RunRequest.input`` must accept a *structured* (dict) value,
    not only text. Handler agents (the CI workers) send a serialized WorkerRequest
    as ``input``; an over-strict ``input: str`` schema rejected them with HTTP 422.
    """
    structured = RunRequest(input={"repo": "acme/widget", "n": 1})
    assert structured.model_dump()["input"] == {"repo": "acme/widget", "n": 1}
    assert RunRequest(input="echo hello").input == "echo hello"  # plain text still works


def test_agent_can_supply_a_custom_console():
    """The GET / console is overridable per agent (e.g. the orchestrator's repo-URL UI)."""
    assert Agent(name="t", prompt="x", console_html="<h1>custom</h1>").console_html == "<h1>custom</h1>"
