# Agent Guidelines for {{ cookiecutter.project_name }}

This document provides operational rules, architectural invariants, and verification standards for AI coding agents working on **{{ cookiecutter.project_name }}**.

---

## 1. Operational Boundaries

| Tier | Directives |
| :--- | :--- |
| **Always** | Encapsulate all API transport logic (views, serializers, filters, endpoint routing) inside an `<app>/api/` package; run scoped checks during iteration; write behavior-driven tests alongside code; satisfy the Definition of Done before finishing. |
| **Ask First** | Adding dependencies (`pyproject.toml`); altering settings or auth/permission rules; creating destructive migrations. |
| **Never** | Create flat `views.py`, `serializers.py`, or endpoint `urls.py` at the app root level; edit already-applied migrations; edit/overwrite `.env` or commit secrets; run `manage.py dev` synchronously as a blocking command; commit or push git changes unless explicitly asked. |

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

### 3.1 App Package Layout & Invariants
Every app exposing HTTP/REST endpoints must isolate transport logic within an `api/` sub-package. Creating flat `views.py`, `serializers.py`, or endpoint `urls.py` at the app root is strictly forbidden:

```
<app_name>/
├── api/                     # HTTP transport layer
│   ├── __init__.py
│   ├── views.py             # Thin views (auth/permissions, call services)
│   ├── serializers.py       # Payload validation & serialization only
│   ├── urls.py              # Endpoint routing
│   └── filters.py           # django-filter backends (when applicable)
├── services/                # Pure business logic layer
│   ├── __init__.py
│   └── <name>_service.py    # Zero HTTP request objects
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # API & transport tests
│   ├── test_models.py       # Model & constraint tests
│   └── test_services.py     # Domain service tests
├── factories.py             # Factory Boy fixtures
├── models.py                # Database schema only
├── admin.py
└── apps.py
```

**Dependency Flow Rules:**
- `api/` $\rightarrow$ imports from `services/` and `models.py`.
- `services/` $\rightarrow$ imports from `models.py`, but **never** imports from `api/`.
- `models.py` $\rightarrow$ **never** imports from `services/` or `api/`.

### 3.2 Service Layer Invariant
- **Business logic belongs strictly in `services/`** (e.g., `user_service.py`), NOT in views, serializers, or models.
- **No `request` in services**: Never pass the HTTP `request` object into service functions. Accept typed primitives, domain dataclasses, or model instances to keep services reusable across API views, background workers, and management commands.
- **Views (`api/views.py`)**: Pure HTTP transport layer. Extract parameters, verify permissions (`permission_classes`), validate input with serializers, call domain services, and return standard HTTP status codes (`200`, `201`, `204`, `400`, `401`, `403`, `404`).
- **Serializers (`api/serializers.py`)**: Format translation and payload validation only. Never trigger emails, external API calls, or background tasks in `serializer.save()`.

{%- if cookiecutter.use_huey == "yes" %}
### 3.3 Huey Tasks & The `transaction.on_commit` Invariant
- Background tasks live in `tasks.py` within each domain app and **must be idempotent**.
- **Critical Gotcha**: When dispatching background tasks from inside an atomic database block (`@transaction.atomic`), **always** enqueue using `transaction.on_commit(lambda: my_task(...))` to prevent race conditions where workers execute before the database transaction has committed.
{%- endif %}

### 3.4 Signals Anti-Pattern
- **Never use Django signals for core business workflows** (no emails, user creation, or status changes in `post_save`). Signals obscure control flow and trigger unpredictably during testing, bulk queries, and migrations.
- Signals are reserved strictly for decoupled infrastructure hooks (e.g., cache invalidation on save, deleting files on disk via `post_delete`).

### 3.5 Custom User & Model Invariants
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

## 7. Definition of Done

Before declaring any task complete, verify:

1. **Package Invariant Check**: All API transport files (views, serializers, URLs) reside in `<app>/api/` packages. No flat `views.py` or `serializers.py` exist at app root level.
2. **Code Quality**: `uv run pre-commit run --all-files` passes with 0 errors.
3. **Migrations Check**: `uv run python manage.py makemigrations --check --dry-run` passes.
4. **Test Suite**: `uv run pytest` passes 100% with zero regressions.

---

## 8. Git Commits

### When to commit
- Commit only when explicitly asked. Never push, amend, rebase, or force-push unless asked.
- Before committing, complete the Section 7 checklist. Never bypass hooks with `--no-verify`.

### What goes into a commit
- **One logical change per commit.** If a task touches unrelated things (a bug fix and a refactor), make separate commits.
- **Stage explicit paths.** Never use `git add .` or `git add -A`. Review `git status` and `git diff --staged` before committing.
- **Keep together, in the same commit:**
  - A model change and its generated migration.
  - A behavior change and its tests.
  - A dependency change in `pyproject.toml` and the updated `uv.lock`.
  - A new environment variable and its `.env.example` (and `.env.test` if needed) entry.
- **Never commit:** `.env`, local databases (`db.sqlite3`), `.venv/`, `__pycache__/`, coverage output, uploaded media, editor files, or anything containing secrets.
- **No drive-by changes.** If `ruff format` reformats files unrelated to the task, revert those files or put them in a separate `style:` commit.
- Never edit a migration that has already been committed or applied. Create a new one.

### Message format
```
<type>(<scope>): <subject>

<body: what changed and why, wrapped at 72 chars>

<footer: issue refs, BREAKING CHANGE>
```

- **Branch Naming**: `feat/<topic>`, `fix/<topic>`, `refactor/<topic>`.
- **Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`, `ci`, `perf`, `style`.
- **Scope:** the app or area, e.g. `accounts`, `config`, `deps`.
- **Subject:** imperative mood ("add", not "added"), lowercase, no trailing period, 50 characters or fewer.
- **Body:** optional for trivial changes. Otherwise explain *why*, not what. The diff already shows what.
- **Breaking changes:** add a `BREAKING CHANGE:` footer describing the migration path.

Examples:
```
feat(accounts): add email verification service

Move verification logic out of the serializer so it can be reused
by the management command and the Huey task.

fix(accounts): prevent duplicate users on case-differing emails

chore(deps): bump djangorestframework to 3.16
```
