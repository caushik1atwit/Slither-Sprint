run:
	PYTHONPATH=./src/slither_sprint uv run slither-sprint

format:
	uv run ruff format .

lint:
	uv run ruff check .
