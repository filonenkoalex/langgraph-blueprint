# Agentic App

Agentic application built with LangGraph using the PyStrict template for maximum code quality and strict type checking.

## Setup

This project uses the PyStrict template with ultra-strict Python development practices inspired by TypeScript's `--strict` mode.

### Prerequisites

- [uv](https://github.com/astral-sh/uv) - Python package manager
- Python 3.12+ (managed by uv)

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd C:\Projects\langgraph-blueprint
   ```

2. Create and activate the virtual environment (already done):
   ```bash
   # On Windows
   .venv\Scripts\activate

   # On Linux/macOS
   source .venv/bin/activate
   ```

3. Install dependencies (already done):
   ```bash
   uv pip install -e ".[dev]"
   ```

## Available Commands

### Daily Workflow

```bash
# Format code
uv run ruff format .

# Lint and auto-fix
uv run ruff check . --fix

# Strict type checking
uv run basedpyright

# Run tests with coverage
uv run pytest
```

### Poe Tasks (Task Runner)

```bash
# Format, lint (with auto-fix), and strict type check
uv run poe format

# Lint + strict type check (no auto-fix)
uv run poe check

# Lint only (with auto-fix)
uv run poe lint

# Lint with unsafe fixes
uv run poe lint-unsafe

# Quality metrics (dead code, complexity, maintainability)
uv run poe metrics

# Full quality pipeline (format + lint + type check + metrics)
uv run poe quality
```

## Strictness Features

This project enforces:

- **No implicit Any** - Unknown/untyped values are treated as errors
- **Required type annotations** on function parameters and return types
- **Unused imports/variables/functions** are treated as errors
- **Optional values** (`None`) must be handled explicitly
- **Security-oriented checks** via flake8-bandit rules
- **Coverage threshold** enforced by default (80%)
- **Max complexity**: 10 (McCabe)
- **Max nested blocks**: 3

## Project Structure

```
.
├── src/
│   └── agentic_app/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_example.py
├── pyproject.toml
├── .gitignore
└── .pre-commit-config.yaml
```

## Pre-commit Hooks

The project includes pre-commit hooks configured in `.pre-commit-config.yaml`:

- **Commit**: ruff-format + ruff check --fix
- **Push**: ruff check + basedpyright strict type-check

To enable pre-commit hooks:

```bash
uv pip install pre-commit
pre-commit install
```

## Development

When writing code:

1. **Always use Pydantic models for all I/O** - Never work with raw dictionaries
2. **Avoid boolean traps** - Use enums or keyword-only arguments
3. **Keep functions simple** - Refactor when complexity > 10 or nesting > 3
4. **No bare excepts** - Catch specific exceptions only
5. **All functions must have type annotations**

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_example.py

# Run with verbose output
uv run pytest -v
```

## License

MIT
