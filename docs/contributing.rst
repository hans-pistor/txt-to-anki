Contributing
============

We welcome contributions to txt-to-anki! This guide will help you get started.

Development Setup
-----------------

1. Clone the repository:

.. code-block:: bash

   git clone <repository-url>
   cd txt-to-anki

2. Install Poetry if you haven't already:

.. code-block:: bash

   curl -sSL https://install.python-poetry.org | python3 -

3. Install dependencies:

.. code-block:: bash

   poetry install

Development Workflow
--------------------

Code Quality Standards
~~~~~~~~~~~~~~~~~~~~~~~

This project enforces strict code quality standards:

* **Type checking**: All code must pass mypy with strict settings
* **Formatting**: Code must be formatted with Black
* **Linting**: Code must pass Ruff checks
* **Testing**: All code must have tests with good coverage

Running Quality Checks
~~~~~~~~~~~~~~~~~~~~~~~

Before submitting changes, run all quality checks:

.. code-block:: bash

   # Type checking (REQUIRED - no commits without passing)
   poetry run mypy src/

   # Code formatting
   poetry run black .

   # Linting
   poetry run ruff check .

   # Tests with coverage
   poetry run pytest

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

To build the documentation locally:

.. code-block:: bash

   # Install documentation dependencies
   poetry install

   # Build HTML documentation
   poetry run sphinx-build -b html docs docs/_build/html

   # View documentation
   open docs/_build/html/index.html

Type Hints Requirement
~~~~~~~~~~~~~~~~~~~~~~~

**CRITICAL**: All functions, methods, and variables MUST have type hints. This is enforced by mypy in strict mode. No code will be accepted without proper type annotations.

Example of properly typed code:

.. code-block:: python

   from __future__ import annotations

   def process_text(input_text: str, max_length: int = 100) -> list[str]:
       """Process input text and return list of sentences.

       Args:
           input_text: The text to process
           max_length: Maximum length per sentence

       Returns:
           List of processed sentences
       """
       sentences: list[str] = input_text.split('.')
       return [s.strip() for s in sentences if s.strip()]

Submitting Changes
------------------

1. Create a new branch for your feature or bugfix
2. Make your changes following the code quality standards
3. Add or update tests as needed
4. Update documentation if necessary
5. Run all quality checks and ensure they pass
6. Submit a pull request with a clear description

Testing
-------

Write tests for all new functionality:

.. code-block:: bash

   # Run tests
   poetry run pytest

   # Run tests with coverage report
   poetry run pytest --cov=src --cov-report=html

Tests should be placed in the ``tests/`` directory and follow the naming convention ``test_*.py``.

Documentation
-------------

Update documentation when adding new features:

* Add docstrings to all functions and classes (Google style)
* Update relevant .rst files in the ``docs/`` directory
* Build and review documentation locally before submitting

Questions?
----------

If you have questions about contributing, please open an issue on the project repository.
