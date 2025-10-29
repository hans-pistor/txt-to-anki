# txt-to-anki

A CLI tool for converting plain text files into Anki deck formats for spaced repetition learning.

## Installation

### Using pipx (Recommended)

```bash
pipx install txt-to-anki
```

### Using pip

```bash
pip install txt-to-anki
```

## Usage

Convert a text file to Anki deck format:

```bash
txt-to-anki convert input.txt
```

Specify a custom output file:

```bash
txt-to-anki convert input.txt --output my-deck.apkg
```

## Development

### Prerequisites

- Python 3.10+
- Poetry

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd txt-to-anki
```

2. Install dependencies:
```bash
poetry install
```

3. Run the application:
```bash
poetry run txt-to-anki convert sample.txt
```

### Development Commands

- **Run tests**: `poetry run pytest`
- **Format code**: `poetry run black .`
- **Lint code**: `poetry run ruff check .`
- **Type check**: `poetry run mypy src/`
- **Build package**: `poetry build`

### Code Quality

This project enforces strict type checking with mypy. All functions, methods, and variables must have proper type annotations.

## License

[Add your license here]
