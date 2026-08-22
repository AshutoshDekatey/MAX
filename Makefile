.PHONY: install generate test lint app

install:
	python -m pip install -e ".[dev]"

generate:
	python -m project_max.cli generate --output source-systems/sample-data/v0-demo --include-defects

test:
	python -m pytest

lint:
	python -m ruff check .

app:
	python -m streamlit run frontend/streamlit/app.py

