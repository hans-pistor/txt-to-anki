# Development Guide

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

## Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality. The hooks will run automatically on `git commit` and include:

- **Black**: Code formatting
- **Ruff**: Linting and auto-fixes
- **mypy**: Type checking (strict mode)
- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml**: Validate YAML files
- **check-added-large-files**: Prevent large files from being committed
- **check-merge-conflict**: Detect merge conflict markers

### Running Hooks Manually

Run all hooks on all files:
```bash
poetry run pre-commit run --all-files
```

Run a specific hook:
```bash
poetry run pre-commit run black --all-files
poetry run pre-commit run mypy --all-files
```

## Code Quality Commands

### Type Checking
```bash
poetry run mypy src/
```

### Formatting
```bash
poetry run black .
```

### Linting
```bash
poetry run ruff check .
poetry run ruff check . --fix  # Auto-fix issues
```

### Testing
```bash
poetry run pytest
poetry run pytest --cov=src  # With coverage
poetry run pytest -v  # Verbose output
```

## Development Workflow

1. Make your changes
2. Run tests: `poetry run pytest`
3. The pre-commit hooks will run automatically on commit
4. If hooks fail, fix the issues and commit again
5. Push your changes

## Skipping Hooks (Not Recommended)

If you need to skip hooks temporarily:
```bash
git commit --no-verify
```

**Note**: This should only be used in exceptional circumstances.
