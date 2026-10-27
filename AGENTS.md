# AI Agent Guidelines for Cookie Cutter Django Lean

This document provides operational rules, architectural invariants, and verification standards for AI coding agents maintaining this **Cookiecutter Django Lean** template repository.

---

## 1. Operational Boundaries

| Tier | Directives |
| :--- | :--- |
| **Always** | <ul><li>Preserve Jinja template conditionals (`{% if ... %}`)</li><li>Enforce `<app>/api/` package structure for all app HTTP layers</li><li>Test end-to-end generation before declaring done</li><li>Mirror changes across `cookiecutter.json`, template files, and `hooks/post_gen_project.py`</li></ul> |
| **Ask First** | <ul><li>Adding/removing template configuration choices in `cookiecutter.json`</li><li>Altering supported Python/Django versions</li><li>Removing bundled architectural layers</li></ul> |
| **Never** | <ul><li>Hardcode project values into `{{cookiecutter.project_slug}}/`</li><li>Create flat `views.py` or `serializers.py` at app root level</li><li>Touch or commit secrets or `.env` files</li><li>Run `git commit` or `git push` unless explicitly asked</li></ul> |

---

## 2. Template Architecture & Rules

### 2.1 Preserving Jinja Template Syntax
- Files inside `{{cookiecutter.project_slug}}/` contain Jinja syntax (e.g., `{% if cookiecutter.use_rest_framework == "yes" %}`).
- **Always preserve conditional blocks** when editing template files. Never strip feature conditionals unless explicitly instructed.
- When introducing a new feature or dependency:
  1. `cookiecutter.json` (define variable and default choices)
  2. `{{cookiecutter.project_slug}}/pyproject.toml` (specify dependencies)
  3. `hooks/post_gen_project.py` (post-generation cleanup or environment generation)
  4. Both `README.md` files (root and template)

### 2.2 Django Architectural Invariants for Template Apps
- **App Package Layout**: Every app exposing HTTP transport logic must encapsulate views, serializers, filters, and routing inside an `api/` package (`<app>/api/`). Flat `views.py` or `serializers.py` at the app root are strictly forbidden.
- **Dependency Flow**: `api/` imports from `services/` and `models.py`. `services/` imports from `models.py` (never `api/`). `models.py` never imports from `services/` or `api/`.
- **Service Layer First**: Business logic must reside strictly in `services/` (e.g. `user_service.py`), keeping API views, serializers, and models thin.
- **No `request` in services**: Never pass the HTTP `request` object into service layer functions.
- **QuerySets & Managers**: Encapsulate reusable filtering, aggregations, and optimizations (`select_related`, `prefetch_related` to eliminate N+1 queries) in custom `models.QuerySet` methods. Authorization and tenant filtering belongs in `get_queryset()`, not `filters.py`.
- **Settings Hierarchy**: Environment settings are split under `config/settings/` (`base.py`, `local.py`, `prod.py`, `test.py`, `__init__.py`). Resolve via `DJANGO_ENV` and `python-decouple`.
- **User Model Invariant**: Use `get_user_model()` in code and `settings.AUTH_USER_MODEL` in model foreign keys. Never import the User model directly from app models across apps.
- **Signals**: Never use signals for business logic (emails, payments, user creation). Reserved strictly for decoupled infrastructure hooks (cache clearing, file deletion on `post_delete`).

---

## 3. Testing Conventions

- **File Naming & Location**: App tests live in `tests/` with `__init__.py`, prefixed with `test_` (`test_models.py`, `test_services.py`, `test_api.py`, `test_architecture.py`).
- **Naming Pattern**: Behavior-driven naming: `test_<action>_<expected_outcome>_<condition>`.
- **Assertions**: Multiple `assert` statements are allowed when verifying facets of a single behavior.
- **Factory Boy**: Use factories from `factories.py` with distinct emails/identifiers to prevent `django_get_or_create` deduplication collisions.
- **Fast & Isolated**: Test settings use in-memory SQLite (`:memory:`) and `MD5PasswordHasher` with zero network I/O.

---

## 4. Definition of Done

Before declaring any task complete:

1. **Verify Template Generation & Tests**:
   ```bash
   mkdir -p /tmp/cookiecutter_test && cd /tmp/cookiecutter_test
   rm -rf test_proj
   uvx cookiecutter "<path_to_template_root>" --no-input project_slug="test_proj"
   cd test_proj
   uv run pre-commit run --all-files
   uv run pytest
   cd .. && rm -rf test_proj
   ```
2. **Repository Cleanliness**: Ensure 0 pre-commit errors and 0 test failures.

---

## 5. Git Commits

### When to commit
- Commit only when explicitly asked. Never push, amend, rebase, or force-push unless asked.
- Before committing, complete the Section 4 checklist. Never bypass hooks with `--no-verify`.

### What goes into a commit
- **One logical change per commit.** If a task touches unrelated things, make separate commits.
- **Stage explicit paths.** Never use `git add .` or `git add -A`. Review `git status` and `git diff --staged` before committing.
- **Keep together, in the same commit:**
  - A template option change and its updates across `cookiecutter.json`, template files, and `hooks/post_gen_project.py`.
  - A dependency or architecture change and its corresponding tests/documentation.
- **Never commit:** secrets, `.env`, scratch directories, or temporary test projects.
- **No drive-by changes.** If `ruff format` reformats files unrelated to the task, revert those files or put them in a separate `style:` commit.

### Branch Naming
`feat/<topic>`, `fix/<topic>`, `refactor/<topic>`.

### Message format
```
<type>(<scope>): <subject>

<body: what changed and why, wrapped at 72 chars>

<footer: issue refs, BREAKING CHANGE>
```

- **Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`, `ci`, `perf`, `style`.
- **Scope:** e.g. `template`, `hooks`, `docs`, `deps`.
- **Subject:** imperative mood ("add", not "added"), lowercase, no trailing period, 50 characters or fewer (max 72).
- **Body:** optional for trivial changes. Otherwise explain *why*, not what.
- **Breaking changes:** add a `BREAKING CHANGE:` footer describing the migration path.
