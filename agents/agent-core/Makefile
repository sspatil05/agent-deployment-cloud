.PHONY: install test lint build publish

install:
	uv sync --extra dev --extra service

test:
	uv run pytest -q

lint:
	uv run ruff check .

build:
	uv build

publish:
	uv publish
