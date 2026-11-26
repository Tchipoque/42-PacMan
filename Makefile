
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run python3 pac-man.py config.json

debug:
	uv run python3 -m pdb pac-man.py config.json

# Remove cache files
clean:
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	uv run python3 -m flake8 . --exclude=.venv
	uv run python3 -m mypy . --exclude '.venv' $(MYPY_FLAGS)

lint-strict:
	uv run python3 -m flake8 . --exclude=.venv
	uv run python3 -m mypy . --exclude '.venv' --strict

