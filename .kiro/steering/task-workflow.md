# Automated Task Workflow

When implementing tasks from `.kiro/specs/*/tasks.md`, ALWAYS follow this complete workflow:

## ⚠️ CRITICAL: PRE-IMPLEMENTATION CHECKLIST ⚠️

**Before writing ANY code, complete these steps IN ORDER:**

- [ ] 1. Read the task from tasks.md
- [ ] 2. Create GitHub issue using `gh issue create`
- [ ] 3. Note the issue number (e.g., #42)
- [ ] 4. Create feature branch: `git checkout -b feature/<issue-number>-<description>`
- [ ] 5. NOW you can start coding

**DO NOT SKIP STEP 2! GitHub issue creation is MANDATORY before any code changes.**

## 1. Before Starting Implementation

1. **Create GitHub Issue** (MANDATORY FIRST STEP):
   - **DO THIS FIRST** before any code changes
   - Use the task title and details to create a descriptive issue
   - Follow the issue template from `github-workflow.md`
   - Include acceptance criteria from the task
   - Note the issue number (e.g., #42)
   - **STOP and wait for issue creation before proceeding**

2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/<issue-number>-<short-description>
   ```
   Example: `feature/42-file-processing-capabilities`

## 2. During Implementation

1. **Implement the feature** following all requirements
2. **Run quality checks** (REQUIRED):
   ```bash
   poetry run mypy src/        # Must pass!
   poetry run black .
   poetry run ruff check .
   poetry run pytest --cov=src
   ```

## 3. After Implementation

1. **Stage changes**:
   ```bash
   git add <modified-files>
   ```

2. **Commit with conventional format**:
   ```bash
   git commit -m "feat(scope): description

   Detailed explanation of changes.

   Closes #<issue-number>"
   ```

3. **Push branch**:
   ```bash
   git push origin feature/<issue-number>-<description>
   ```

4. **Create Pull Request**:
   - Use `gh pr create` or GitHub web interface
   - Fill out PR template
   - Link to issue with "Closes #<issue-number>"
   - Request reviews if needed

5. **Update task status**:
   - Mark task as completed in tasks.md

## Commit Message Format

Follow Conventional Commits:
- `feat(tokenizer): add file processing capabilities`
- `fix(cli): handle missing input file gracefully`
- `test(parser): add edge case tests for empty input`
- `docs(readme): update installation instructions`

## Example Complete Workflow

```bash
# 1. Create issue (note the number, e.g., #42)
gh issue create --title "feat(tokenizer): add file processing" --body-file .github/issue-template.md

# 2. Create branch
git checkout -b feature/42-file-processing

# 3. Implement feature
# ... make code changes ...

# 4. Run quality checks
poetry run mypy src/
poetry run black .
poetry run ruff check .
poetry run pytest

# 5. Commit
git add src/txt_to_anki/tokenizer/japanese_tokenizer.py tests/test_tokenizer.py
git commit -m "feat(tokenizer): add file processing capabilities

Implements tokenize_file method with UTF-8 validation,
comprehensive error handling, and full test coverage.

Closes #42"

# 6. Push and create PR
git push origin feature/42-file-processing
gh pr create --title "feat(tokenizer): add file processing capabilities" --body "Closes #42"
```

## Important Notes

- **🚨 CRITICAL: Create the GitHub issue FIRST, before ANY code changes 🚨**
- **ALWAYS create a feature branch from main**
- **ALWAYS run mypy before committing** (blocking requirement)
- **ALWAYS reference the issue in commits and PRs**
- **NEVER commit directly to main**
- **NEVER skip quality checks**
- **NEVER start coding without a GitHub issue number**

This workflow ensures:
- Traceable changes linked to issues
- Clean git history
- Code quality standards maintained
- Proper documentation of work
