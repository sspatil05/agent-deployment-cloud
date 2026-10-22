# Builds the agent image from the two projects in this folder (build context = agents/):
#   agent-core     the framework library
#   agent-starter  the agent itself (prompt, skills, tools)
#
# agent-core is installed from the local copy instead of the git URL named in agent-starter/pyproject.toml, so the
# build needs no network access to GitHub and always uses exactly the code in this repository.
# agent-starter is installed with --no-deps so pip does not try to re-fetch that git dependency.
FROM python:3.11-slim AS build
WORKDIR /src
COPY agent-core ./agent-core
COPY agent-starter ./agent-starter
RUN pip install --no-cache-dir "./agent-core[anthropic,openrouter]" \
 && pip install --no-cache-dir --no-deps ./agent-starter

FROM python:3.11-slim AS runtime
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin agent
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
USER 10001
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
ENTRYPOINT ["agent"]
