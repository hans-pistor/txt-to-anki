---
inclusion: always
---

# GitHub Workflow Standards

## Overview

This document establishes the Git and GitHub workflow standards for the txt-to-anki project. Following these practices ensures clean history, traceable changes, and collaborative development.

## Branch Strategy

### Main Branches

- **`main`**: Production-ready code only
  - Protected branch with required reviews
  - All commits must pass CI/CD checks
  - Direct commits prohibited
  - Deployable at any time

- **`develop`**: Integration branch for features (optional, use if needed)
  - Use only for larger projects with multiple concurrent features
  - For this project, feature branches can merge directly to `main`

### Feature Branches

**Naming Convention**: `feature/<issue-number>-<short-description>`

Examples:
- `feature/42-japanese-tokenizer`
- `feature/15-anki-export-format`
- `feature/8-cli-help-text`

**Rules**:
- Always branch from `main`
- One feature/issue per branch
- Keep branches short-lived (< 1 week ideal)
- Delete after merging

### Bug Fix Branches

**Naming Convention**: `fix/<issue-number>-<short-description>`

Examples:
- `fix/23-encoding-error`
- `fix/56-missing-type-hints`

### Other Branch Types

- `docs/<description>`: Documentation-only changes
- `refactor/<description>`: Code refactoring without behavior changes
- `test/<description>`: Test additions or improvements
- `chore/<description>`: Maintenance tasks (dependencies, tooling)

## Issue-Driven Development

### Creating Issues

**Every feature, bug, or task MUST have a GitHub issue before work begins.**

#### Issue Template Structure

**For Features**:
```markdown
## Description
[Clear description of the feature]

## User Story
As a [user type], I want [goal] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
[Any technical considerations]

## Definition of Done
- [ ] Code implemented
- [ ] Type hints added (mypy passes)
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] PR reviewed and approved
```

**For Bugs**:
```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- Python version:
- OS:
- Package version:

## Possible Solution
[Optional: suggestions for fixing]
```

#### Issue Labels

Use these standard labels:
- `feature`: New functionality
- `bug`: Something isn't working
- `documentation`: Documentation improvements
- `enhancement`: Improvement to existing feature
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `priority: high/medium/low`: Priority level
- `type-checking`: Related to mypy/type hints
- `testing`: Related to tests

### Issue Assignment

- Assign yourself before starting work
- Comment on the issue when you begin
- Link the issue in your branch name
- Reference the issue in commits and PRs

## Commit Standards

### Commit Message Format

Follow Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

#### Examples

```
feat(tokenizer): add Japanese text tokenization support

Implements MeCab-based tokenization for Japanese text with
proper handling of kanji, hiragana, and katakana.

Closes #42
```

```
fix(cli): handle missing input file gracefully

Previously crashed with unhandled exception. Now provides
clear error message and exits with code 2.

Fixes #23
```

```
test(parser): add edge case tests for empty input

Closes #56
```

### Commit Best Practices

- **Atomic commits**: One logical change per commit
- **Type hints required**: All commits must maintain mypy compliance
- **Present tense**: "Add feature" not "Added feature"
- **Imperative mood**: "Fix bug" not "Fixes bug"
- **Reference issues**: Use "Closes #123" or "Fixes #123" in footer
- **Keep subject under 72 characters**
- **Explain why, not what**: Body should explain reasoning

## Pull Request Workflow

### Creating Pull Requests

1. **Ensure all checks pass locally**:
   ```bash
   poetry run mypy src/        # REQUIRED - must pass
   poetry run black .
   poetry run ruff check .
   poetry run pytest --cov=src
   ```

2. **Push feature branch**:
   ```bash
   git push origin feature/42-japanese-tokenizer
   ```

3. **Create PR with template**:

```markdown
## Description
[Clear description of changes]

## Related Issue
Closes #42

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows project style guidelines
- [ ] Type hints added (mypy passes) ✅ REQUIRED
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings

## Testing
[Describe testing performed]

## Screenshots (if applicable)
[Add screenshots for UI changes]
```

### PR Best Practices

- **Small PRs**: Aim for < 400 lines changed
- **Single purpose**: One feature/fix per PR
- **Draft PRs**: Use for work-in-progress to get early feedback
- **Link issues**: Use "Closes #123" in description
- **Request reviews**: Tag specific reviewers
- **Respond to feedback**: Address all comments
- **Keep updated**: Rebase or merge main regularly

### Review Requirements

- **Minimum 1 approval** required for merge
- **All CI checks must pass** (including mypy)
- **No unresolved conversations**
- **Branch must be up-to-date with main**

### Merge Strategy

- **Squash and merge**: For feature branches (preferred)
  - Creates clean, linear history
  - Combines all commits into one
  - Use for most features

- **Rebase and merge**: For small, clean commits
  - Preserves individual commits
  - Use when commits are already well-structured

- **Never use merge commits** unless absolutely necessary

## Development Workflow Example

### Complete Feature Workflow

```bash
# 1. Create issue on GitHub (e.g., #42)

# 2. Create and checkout feature branch
git checkout main
git pull origin main
git checkout -b feature/42-japanese-tokenizer

# 3. Make changes with atomic commits
git add src/txt_to_anki/tokenizer.py
git commit -m "feat(tokenizer): add base tokenizer interface

Closes #42"

# 4. Run quality checks (REQUIRED)
poetry run mypy src/        # Must pass!
poetry run black .
poetry run ruff check .
poetry run pytest --cov=src

# 5. Push branch
git push origin feature/42-japanese-tokenizer

# 6. Create PR on GitHub
# - Fill out PR template
# - Link to issue #42
# - Request reviews

# 7. Address review feedback
git add .
git commit -m "refactor(tokenizer): improve error handling per review"
git push origin feature/42-japanese-tokenizer

# 8. After approval and CI passes, squash and merge

# 9. Delete branch
git checkout main
git pull origin main
git branch -d feature/42-japanese-tokenizer
git push origin --delete feature/42-japanese-tokenizer

# 10. Close issue (auto-closed by "Closes #42" in PR)
```

## CI/CD Integration

### Required Checks

All PRs must pass:
- **mypy type checking** (REQUIRED - blocking)
- Black formatting check
- Ruff linting
- pytest with coverage (minimum 80%)
- Build verification

### GitHub Actions Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH

    - name: Install dependencies
      run: poetry install

    - name: Type check with mypy (REQUIRED)
      run: poetry run mypy src/

    - name: Format check with Black
      run: poetry run black --check .

    - name: Lint with Ruff
      run: poetry run ruff check .

    - name: Test with pytest
      run: poetry run pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Branch Protection Rules

Configure on GitHub for `main` branch:

- ✅ Require pull request reviews before merging (1 approval)
- ✅ Require status checks to pass before merging
  - mypy type checking (REQUIRED)
  - Black formatting
  - Ruff linting
  - pytest
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings
- ✅ Restrict who can push to matching branches
- ✅ Require linear history (squash or rebase only)

## Release Workflow

### Versioning

Follow Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes (v2.0.0)
- **MINOR**: New features, backward compatible (v1.1.0)
- **PATCH**: Bug fixes, backward compatible (v1.0.1)

### Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create release branch**: `release/v1.2.0`
4. **Create PR to main**
5. **After merge, create Git tag**:
   ```bash
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   ```
6. **Create GitHub Release** with changelog
7. **Publish to PyPI**: `poetry publish --build`

## Quick Reference

### Common Commands

```bash
# Start new feature
git checkout main && git pull
git checkout -b feature/<issue>-<description>

# Quality checks before commit
poetry run mypy src/        # REQUIRED
poetry run black .
poetry run ruff check .
poetry run pytest

# Commit with conventional format
git commit -m "feat(scope): description

Closes #<issue>"

# Update branch with main
git checkout main && git pull
git checkout feature/<branch>
git rebase main

# Clean up after merge
git branch -d feature/<branch>
git push origin --delete feature/<branch>
```

---

**Remember**: Type checking with mypy is REQUIRED. No PR will be merged without passing type checks.
