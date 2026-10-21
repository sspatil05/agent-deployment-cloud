# agent-core

The shared framework every agent depends on. **Agents never copy this code** —
they install it as a versioned package (`agent-core==x.y`). Change it here, tag a
release, and every agent picks it up on its next version bump. That is what keeps
every agent identical.

## What's inside

| Module | Role |
|---|---|
| `agent.py` | the `Agent` assembly object (prompt + skills + tools) |
| `tools.py` | the `Tool` base class — *code* the LLM can call |
| `skills.py` | loads *markdown* skill docs into the system prompt |
| `brain.py` | the LLM tool-use loop (model orchestrates the tools) |
| `runtime.py` | starts the HTTP service (every agent is a server) |
| `service.py` | FastAPI factory + health/metrics endpoints |
| `intake.py` | request acceptance (validate incoming events) |
| `manager.py` | orchestrates a run (brain loop, or a custom handler) |
| `monitoring.py` | metrics / health (the "line graphs") |
| `connections/` | connectors — `http` ships in core; `jira`/`slack`/`github`/`k8s` are extras |
| `llm/` | the model client (Claude tool-use; keyless NoOp for local runs) |
| `messaging.py` + `contracts/` | dormant seam for future agent-to-agent comms |

## Develop

```bash
pip install uv            # if you don't have it: https://docs.astral.sh/uv/
uv sync --extra dev
uv run pytest
```

## Release

Tag `vX.Y.Z` and push — `.github/workflows/publish.yml` builds and publishes the
package. Agents then bump `agent-core==X.Y.Z` to adopt it.
