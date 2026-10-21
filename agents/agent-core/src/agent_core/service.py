"""FastAPI app for every agent: health/metrics, the /run endpoint, and a small
built-in **test console** at ``/`` so any agent is testable in a browser.

FastAPI gives every agent an OpenAPI (Swagger) spec **for free**:
  - Swagger UI   -> GET /docs
  - ReDoc        -> GET /redoc
  - OpenAPI JSON -> GET /openapi.json

The ``/run`` endpoint is typed with pydantic models below, so those docs show the
real request/response schema (not just an opaque body).

Heavy deps (fastapi/uvicorn) are imported lazily so ``import agent_core`` works
without them; they're only needed when an agent actually serves.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from . import monitoring
from .intake import Intake
from .manager import RunManager


class RunRequest(BaseModel):
    """Body for ``POST /run``.

    ``input`` is what the agent works from — free text for an LLM/brain agent, or a
    structured object for a handler agent (e.g. a serialized ``WorkerRequest``). Any
    extra top-level fields are allowed and passed straight through to the agent.
    """

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={"examples": [{"input": "echo hello"}]},
    )
    input: Any = None


class RunResponse(BaseModel):
    agent: str
    result: Any = None


def create_app(agent):
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI(
        title=f"{agent.name} agent",
        version="0.2.0",
        description=(
            f"**{agent.name}** — an agent built on agent-core.\n\n"
            "`POST /run` to invoke it. Interactive docs: `/docs` (Swagger) · `/redoc`."
        ),
    )
    manager = RunManager(agent)
    intake = Intake()

    @app.get("/healthz", tags=["ops"], summary="Liveness probe")
    def healthz():
        return monitoring.healthz()

    @app.get("/readyz", tags=["ops"], summary="Readiness probe")
    def readyz():
        return {"status": "ready", "agent": agent.name}

    @app.get("/metrics", tags=["ops"], summary="Run counters")
    def metrics():
        return monitoring.metrics()

    @app.post("/run", response_model=RunResponse, tags=["agent"], summary="Invoke the agent")
    def run(req: RunRequest) -> RunResponse:
        # req.model_dump() -> {"input": ..., **extra}. intake validates it.
        return manager.run_once(intake.accept(req.model_dump()))

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def console():
        # An agent may ship its own console (e.g. a repo-URL form); else the default.
        return agent.console_html or _CONSOLE_HTML.replace("__AGENT__", agent.name)

    return app


def serve(agent, host: str = "0.0.0.0", port: int = 8080) -> None:
    import uvicorn

    uvicorn.run(create_app(agent), host=host, port=port)


# A tiny self-contained test console served at GET / — no build step, no CDN.
_CONSOLE_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__AGENT__ · test console</title>
<style>
  :root { color-scheme: light dark; }
  body { font: 15px/1.5 system-ui, sans-serif; max-width: 760px; margin: 2rem auto;
         padding: 0 1rem; }
  h1 { font-size: 1.3rem; margin: 0 0 .25rem; }
  h1 span { font-weight: 400; opacity: .55; }
  .links { opacity: .7; font-size: .85rem; margin-bottom: 1rem; }
  textarea { width: 100%; min-height: 92px; font: 13px ui-monospace, monospace;
             padding: .6rem; box-sizing: border-box; border-radius: 8px;
             border: 1px solid #8884; background: #8881; }
  button { margin-top: .6rem; padding: .5rem 1.1rem; font-size: .95rem; cursor: pointer;
           border: 0; border-radius: 8px; background: #3b82f6; color: #fff; }
  pre { margin-top: 1rem; padding: .8rem; background: #8881; border-radius: 8px;
        white-space: pre-wrap; word-break: break-word; min-height: 2rem; }
</style></head>
<body>
  <h1>__AGENT__ <span>· test console</span></h1>
  <div class="links">POST to <code>/run</code> &nbsp;·&nbsp;
    <a href="/docs">/docs</a> &nbsp;·&nbsp; <a href="/healthz">/healthz</a></div>
  <textarea id="in">{"input": "echo hello"}</textarea><br>
  <button id="go">Run &#9654;</button>
  <pre id="out">Response will appear here.</pre>
  <script>
    const btn = document.getElementById('go'),
          out = document.getElementById('out'),
          inp = document.getElementById('in');
    btn.onclick = async () => {
      const raw = inp.value.trim();
      let body;
      try { body = JSON.parse(raw); } catch (e) { body = { input: raw }; }
      out.textContent = 'Running...';
      btn.disabled = true;
      try {
        const r = await fetch('/run', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify(body),
        });
        const t = await r.text();
        let pretty; try { pretty = JSON.stringify(JSON.parse(t), null, 2); } catch { pretty = t; }
        out.textContent = (r.ok ? '' : 'HTTP ' + r.status + '\\n') + pretty;
      } catch (e) { out.textContent = 'Error: ' + e; }
      finally { btn.disabled = false; }
    };
  </script>
</body></html>
"""
