# Agent Guidelines for {{ cookiecutter.project_name }}

This document provides operational rules, architectural invariants, and verification standards for AI coding agents working on **{{ cookiecutter.project_name }}**.

---

## 1. Operational Boundaries

| Tier | Directives |
| :--- | :--- |
| **Always** | Run scoped checks during iteration; write behavior-driven tests alongside code; satisfy the Definition of Done before finishing. |
| **Ask First** | Adding dependencies (`pyproject.toml`); altering settings or auth/permission rules; creating destructive migrations. |
| **Never** | Edit already-applied migrations; edit/overwrite `.env` or commit secrets; run `manage.py dev` synchronously as a blocking command; commit or push git changes unless explicitly asked. |

---

## 2. Tooling & Environment

- **Package Manager**: Exclusively use `uv`.
  - Commands: `uv run python manage.py <command>`
  - Fast test iteration: `uv run pytest path/to/test_x.py -k <filter>`
  - Fast lint iteration: `uv run ruff check path/to/file.py` (or `uv run pre-commit run --files <paths>`)
  - Dependencies: `uv add <package>` (or `uv add --dev <package>`)
- **Settings Selection**: `config/settings/__init__.py` resolves environment automatically:
  - `DJANGO_ENV=production` (or `ENVIRONMENT=production`) $\rightarrow$ `config.settings.prod`
  - Automated tests (`pytest`, `sys.argv`) $\rightarrow$ `config.settings.test`
  - Default (`DEBUG=True` in `.env`) $\rightarrow$ `config.settings.local`
- **Development Server (`manage.py dev`)**:
  - `uv run python manage.py dev` runs the Django dev server and Huey background worker concurrently with auto-restarts.
  - **Agent Directive**: This is a blocking process for human developers. Never run it synchronously during autonomous tasks; use `pytest` for verification.

---

## 3. Architecture & Domain Rules

### 3.1 Service Layer Invariant
- **Business logic belongs strictly in `services/`** (e.g., `user_service.py`), NOT in views, serializers, or models.
- **No `request` in services**: Never pass the HTTP `request` object into service functions. Accept typed primitives, domain dataclasses, or model instances to keep services reusable across API views, background workers, and management commands.
- **Views (`api/views.py`)**: Pure HTTP transport layer. Extract parameters, verify permissions (`permission_classes`), validate input with serializers, call domain services, and return standard HTTP status codes (`200`, `201`, `204`, `400`, `401`, `403`, `404`).
- **Serializers (`api/serializers.py`)**: Format translation and payload validation only. Never trigger emails, external API calls, or background tasks in `serializer.save()`.

{%- if cookiecutter.use_huey == "yes" %}
### 3.2 Huey Tasks & The `transaction.on_commit` Invariant
- Background tasks live in `tasks.py` within each domain app and **must be idempotent**.
- **Critical Gotcha**: When dispatching background tasks from inside an atomic database block (`@transaction.atomic`), **always** enqueue using `transaction.on_commit(lambda: my_task(...))` to prevent race conditions where workers execute before the database transaction has committed.
{%- endif %}

### 3.3 Signals Anti-Pattern
- **Never use Django signals for core business workflows** (no emails, user creation, or status changes in `post_save`). Signals obscure control flow and trigger unpredictably during testing, bulk queries, and migrations.
- Signals are reserved strictly for decoupled infrastructure hooks (e.g., cache invalidation on save, deleting files on disk via `post_delete`).

### 3.4 Custom User & Model Invariants
- Never import `User` directly across apps. Always use `from django.contrib.auth import get_user_model; User = get_user_model()` in code and `settings.AUTH_USER_MODEL` in model foreign keys.
- **Financial / Critical Data**: Always use `Decimal` (never `float`) for monetary amounts and currency fields. Enforce audit trails and idempotent mutations on state-changing operations.

---

## 4. Testing Conventions

- **File Naming & Location**:
  - Locate tests in an app-level `tests/` package (e.g., `accounts/tests/`) with an `__init__.py` (never a single `tests.py`).
  - Prefix filenames with `test_` (`test_models.py`, `test_services.py`, `test_api.py`, `test_tasks.py`).
- **Naming Pattern**: Use behavior-driven names: `test_<action>_<expected_outcome>_<condition>`.
- **Assertions**: Multiple `assert` statements are encouraged in a single test, provided they all verify facets of the same behavior.
- **Factory Boy**: Use factories from `factories.py`. Use distinct emails/unique fields across instances to prevent `django_get_or_create` deduplication collisions.
- **Performance**: Tests run against `config.settings.test` (in-memory SQLite, MD5 hasher). No external network I/O or sleep calls.

---

## 5. Clean Code & Comments

- **Eliminate Noise**: Delete comments that merely restate code (e.g. `# Storage`, `# Email backend`).
- **Explain Intent & Consequences**: Use comments strictly to document non-obvious *why* or warn of subtle consequences.
- Write descriptive, self-documenting identifiers.

---

## 6. Database Migrations

- Always generate migrations via `uv run python manage.py makemigrations`.
- **Zero-Downtime Expand-Contract Pattern**:
  1. *Expand*: Add new column as nullable (`null=True`) or with safe default.
  2. *Migrate*: Deploy code that dual-writes or populates the new column.
  3. *Contract*: Remove old column or add `null=False` in a subsequent migration.

---

## 7. Git & PR Conventions

- **Branch Naming**: `feat/<topic>`, `fix/<topic>`, `refactor/<topic>`.
- **Commit Messages**: Conventional Commits (`feat: ...`, `fix: ...`, `test: ...`, `refactor: ...`, `chore: ...`).
- **Agent Rule**: Do not run `git commit` or `git push` unless explicitly asked by the user.

---

## 8. Definition of Done

Before declaring any task complete, verify:

1. **Code Quality**: `uv run pre-commit run --all-files` passes with 0 errors.
2. **Migrations Check**: `uv run python manage.py makemigrations --check --dry-run` passes.
3. **Test Suite**: `uv run pytest` passes 100% with zero regressions.
