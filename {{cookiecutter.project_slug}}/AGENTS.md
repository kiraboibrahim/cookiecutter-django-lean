# Agent Guidelines for {{ cookiecutter.project_name }}

> {{ cookiecutter.project_description }}

This document provides operational rules, architectural invariants, and verification standards for AI coding agents working on **{{ cookiecutter.project_name }}**.

---

## 1. Operational Boundaries

| Tier | Directives |
| :--- | :--- |
| **Always** | <ul><li>Run scoped checks during iteration (`ruff`, `pytest`)</li><li>Encapsulate all API transport logic (views, serializers, filters, URLs) inside `<app>/api/`</li><li>Write behavior-driven tests alongside code</li><li>Satisfy the Definition of Done before finishing</li></ul> |
| **Ask First** | <ul><li>Adding dependencies (`pyproject.toml`)</li><li>Altering settings, auth, or permission rules</li><li>Creating destructive migrations (dropping tables/columns)</li></ul> |
| **Never** | <ul><li>Create flat `views.py`, `serializers.py`, or endpoint `urls.py` at the app root level</li><li>Edit already-applied migrations</li><li>Edit/overwrite `.env` or commit secrets</li><li>Run `manage.py dev` synchronously as a blocking command</li><li>Commit or push git changes unless explicitly asked</li></ul> |

---

## 2. Tooling & Environment

- **Package Manager**: Exclusively use `uv`.
  - Commands: `uv run python manage.py <command>`
  - Fast test iteration: `uv run pytest path/to/test_x.py -k <filter>`
  - Fast lint iteration: `uv run ruff check path/to/file.py` (or `uv run pre-commit run --files <paths>`)
  - Dependencies: `uv add <package>` (or `uv add --dev <package>`)
- **Settings Resolution**: `config/settings/__init__.py` resolves environments in the following order:
  1. Automated test runs (`pytest`, `sys.argv`) → `config.settings.test`
  2. `DJANGO_ENV=production` → `config.settings.prod`
  3. Default (`DEBUG=True` in `.env`) → `config.settings.local`
- **Configuration & Secrets**:
  - Always load settings and secrets via `python-decouple` (`from decouple import config`). Never hardcode secrets or environment values.
  - When adding a new setting or environment variable, document it in `.env.example` (and `.env.test` if needed) with sensible defaults or placeholders.
- **Development Server (`manage.py dev`)**:
  - `uv run python manage.py dev` runs the Django dev server{% if cookiecutter.use_huey == "yes" %} and Huey background worker{% endif %} concurrently with auto-restarts.
  - **Agent Directive**: This is a blocking process for human developers. Never run it synchronously during autonomous tasks; use `pytest` for verification.

---

## 3. Architecture & Domain Rules

### App Package Layout & Invariants
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
{% if cookiecutter.use_huey == "yes" %}
├── tasks.py                 # Idempotent background tasks
{% endif %}
├── signals.py               # Decoupled infrastructure hooks only
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
- `api/` → imports from `services/` and `models.py`.
- `services/` → imports from `models.py`, but **never** imports from `api/`.
- `models.py` → **never** imports from `services/` or `api/`.

### Service Layer Invariant
- **Business logic belongs strictly in `services/`** (e.g., `user_service.py`), NOT in views, serializers, or models.
- **No `request` in services**: Never pass the HTTP `request` object into service functions. Accept typed primitives, domain dataclasses, or model instances to keep services reusable across API views, background workers, and management commands.
- **Views (`api/views.py`)**: Pure HTTP transport layer. Extract parameters, verify permissions (`permission_classes`), validate input with serializers, call domain services, and return standard HTTP status codes (`200`, `201`, `204`, `400`, `401`, `403`, `404`).
- **Serializers (`api/serializers.py`)**: Format translation and payload validation only. Never trigger emails, external API calls, or background tasks in `serializer.save()`.

### Custom QuerySets & Managers
- **Encapsulate Queries**: Encapsulate reusable query logic, common aggregations, and optimizations (`select_related`, `prefetch_related` to eliminate N+1 queries) in custom `models.QuerySet` methods exposed via `models.Manager.from_queryset()`.
- **Authorization Filtering**: Ownership or multi-tenant filtering belongs in the view's `get_queryset()` method, not in `filters.py`.
- QuerySets handle data retrieval and filtering; Services coordinate mutations and business operations.

{% if cookiecutter.use_huey == "yes" %}
### Huey Tasks & The `transaction.on_commit` Invariant
- Background tasks live in `tasks.py` within each domain app and **must be idempotent**.
- **Critical Gotcha**: When dispatching background tasks from inside an atomic database block (`@transaction.atomic`), **always** enqueue using `transaction.on_commit(lambda: my_task(...))` to prevent race conditions where workers execute before the database transaction has committed.
{% endif %}

### Signals Anti-Pattern
- **Never use Django signals for core business workflows** (no emails, user creation, or status changes in `post_save`). Signals obscure control flow and trigger unpredictably during testing, bulk queries, and migrations.
- Signals are reserved strictly for decoupled infrastructure hooks (e.g., cache invalidation on save, deleting files on disk via `post_delete`).

### Custom User Model Invariant
- Never import `User` directly across apps. Always use `from django.contrib.auth import get_user_model; User = get_user_model()` in code and `settings.AUTH_USER_MODEL` in model foreign keys.

### Financial & Precision Data
- Always use `Decimal` (never `float`) for monetary amounts, financial balances, and currency fields. Enforce audit trails and idempotent mutations on state-changing operations.

---

## 4. Testing Conventions

- **File Naming & Location**:
  - Locate tests in an app-level `tests/` package (e.g., `accounts/tests/`) with an `__init__.py` (never a single `tests.py`).
  - Prefix filenames with `test_` (`test_models.py`, `test_services.py`, `test_api.py`, `test_architecture.py`).
- **Naming Pattern**: Use behavior-driven names: `test_<action>_<expected_outcome>_<condition>`.
- **Assertions**: Multiple `assert` statements are allowed when verifying facets of a single behavior (do not force arbitrary single-assert rules).
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
- **Never edit an applied or committed migration**: Always create a new migration to modify schema or constraints.
- **Zero-Downtime Expand-Contract Pattern**:
  1. *Expand*: Add new column as nullable (`null=True`) or with safe default.
  2. *Migrate*: Deploy code that dual-writes or populates the new column.
  3. *Contract*: Remove old column or add `null=False` in a subsequent migration.

---

## 7. Definition of Done

Before declaring any task complete, verify:

1. **Architecture & Tests**: `uv run pytest` passes 100% with zero regressions (including app package layout invariant tests).
2. **Code Quality**: `uv run pre-commit run --all-files` passes with 0 errors.
3. **Migrations Check**: `uv run python manage.py makemigrations --check --dry-run` passes.

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

### Branch Naming
`feat/<topic>`, `fix/<topic>`, `refactor/<topic>`.

### Message format
```
<type>(<scope>): <subject>

<body: what changed and why, wrapped at 72 chars>

<footer: issue refs, BREAKING CHANGE>
```

- **Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`, `ci`, `perf`, `style`.
- **Scope:** the app or area, e.g. `accounts`, `config`, `deps`.
- **Subject:** imperative mood ("add", not "added"), lowercase, no trailing period, 50 characters or fewer (max 72).
- **Body:** optional for trivial changes. Otherwise explain *why*, not what. The diff already shows what.
- **Breaking changes:** add a `BREAKING CHANGE:` footer describing the migration path.

Examples:

```
feat(accounts): add email verification service

Move verification logic out of the serializer so it can be reused
by the management command{% if cookiecutter.use_huey == "yes" %} and the Huey task{% endif %}.
```

```
fix(accounts): deduplicate case-differing emails

Ensure email uniqueness lookup is case-insensitive during user
registration to prevent duplicate account creation.
```

```
chore(deps): bump djangorestframework to 3.16
```
