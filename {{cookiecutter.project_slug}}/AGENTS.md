# AI Agent Guidelines for {{ cookiecutter.project_name }}

This document provides operational principles, architectural rules, and development conventions for AI coding agents working on **{{ cookiecutter.project_name }}**. Always adhere to these standards when creating, modifying, or refactoring code.

---

## 1. Tooling & Environment Standards

- **Package & Environment Manager**: Exclusively use `uv`. Never run bare `pip` or unmanaged python environments.
  - Run commands: `uv run python manage.py <command>`
  - Run tests: `uv run pytest`
  - Add dependencies: `uv add <package>` (or `uv add --dev <package>` for development dependencies)
  - Synchronize environment: `uv sync --extra dev --extra test`
- **Configuration & Secrets**:
  - Load environment variables using `python-decouple`: `from decouple import config`.
  - Never hardcode secrets or environment-specific values in code.
  - When introducing a new environment variable, declare it with a safe default or placeholder in `.env.example` and update `.env.test` if required for CI/testing.
- **Code Quality & Pre-Commit**:
  - Run all hooks across the codebase: `uv run pre-commit run --all-files`
  - Run linting checks: `uv run ruff check .`
  - Run auto-formatting: `uv run ruff format .`
- **Development Server & Worker Execution**:
  - The canonical command to run the local development environment is:
    ```bash
    uv run python manage.py dev
    ```
    This concurrently manages both the Django dev server and the Huey background worker with auto-restarts and aggregated logging.
  - **Agent Directive**: This is a long-running, blocking process intended for human developers and manual testing. Agents must **not** run this command synchronously during automated tasks; use `uv run pytest` for verification instead. If live HTTP endpoint smoke-testing is explicitly requested, run it as a detached background process and terminate it when done.

---

## 2. Architectural Structure & Design Patterns

The project follows a **modular, service-oriented Django architecture**:

```
{{ cookiecutter.project_slug }}/
├── config/
│   ├── settings/          # Environment-specific settings package
│   │   ├── __init__.py    # Dynamic environment resolver (local, prod, test)
│   │   ├── base.py        # Shared base configuration
│   │   ├── local.py       # Development settings (debug, dev email, sqlite/local DB)
│   │   ├── prod.py        # Production security, storage, S3, email
│   │   └── test.py        # Fast test settings (in-memory sqlite, MD5 hasher)
│   ├── urls.py            # Root URL router
│   ├── wsgi.py            # WSGI entrypoint
│   └── asgi.py            # ASGI entrypoint
{%- if cookiecutter.include_accounts_app == "yes" %}
├── accounts/              # User management & authentication app
│   ├── models.py          # Custom User model & managers (persistence only)
│   ├── admin.py           # Django admin registrations
│   ├── apps.py            # App configuration
│   ├── urls.py            # App-level routing (delegates to api.urls)
│   ├── api/               # HTTP Transport Layer (views, serializers, routes)
│   │   ├── serializers.py # Request/response serialization and validation
│   │   ├── views.py       # Thin API views (authentication, permissions, HTTP status)
│   │   └── urls.py        # Endpoint routing
│   ├── services/          # Domain Layer (core business logic)
│   │   └── user_service.py # Pure domain operations and workflows
│   ├── factories.py       # Factory Boy models for isolated test data
│   └── tests/             # Modular unit and integration tests
│       ├── test_models.py
│       ├── test_services.py
│       └── test_api.py
{%- endif %}
```

### Key Architectural Invariants

1. **Service Layer Pattern**:
   - **Business logic belongs in `services/`**, NOT in views, serializers, or models.
   - Views and serializers should remain thin: parse inputs, authenticate/authorize, invoke domain service methods, and return responses.
   - Models represent state, schema, and basic database constraints. Avoid putting complex cross-model workflows in model methods.
2. **Custom User References**:
   - Never import the User model directly across apps (avoid `from accounts.models import User`).
   - Use `from django.contrib.auth import get_user_model; User = get_user_model()` in code.
   - Use `settings.AUTH_USER_MODEL` in model foreign keys (`ForeignKey(settings.AUTH_USER_MODEL, ...)`).
3. **No Circular Dependencies**:
   - `services/` must never import from `api/`.
   - `models.py` must never import from `services/` or `api/`.

---

## 3. Component Responsibilities & Division of Concerns

To maintain a clean, maintainable, and decoupled codebase, adhere to the following division of responsibilities:

### 3.1 Views (`api/views.py`) — The Transport Layer
- **What belongs in views**:
  - Request extraction (HTTP headers, query params, path arguments, authenticated user).
  - Authentication and permission enforcement (`permission_classes = [IsAuthenticated]`).
  - Serializer invocation for validating input payloads and formatting output data.
  - Calling domain services (`services/`) to execute business workflows, mutations, or side-effects.
  - Returning appropriate HTTP responses with clean status codes (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`).
- **What does NOT belong in views**:
  - Business logic, domain rules, or multi-step mutations.
  - External network calls (third-party APIs, payment gateways, webhooks).
  - Background task enqueueing or transactional email sending.
  - Complex database querying or aggregation logic (delegate to custom QuerySets).

### 3.2 Serializers (`api/serializers.py`) — Data Validation & Serialization
- **When to use**:
  - Converting querysets and models to JSON / Python primitives for HTTP responses.
  - Validating inbound request payloads (data types, formats, required fields, field-level constraints).
  - Basic 1-to-1 model persistence for standard CRUD operations where no external side effects exist.
- **When NOT to use**:
  - Never orchestrate multi-model business workflows in `serializer.save()`, `create()`, or `update()`.
  - Never trigger emails, external API calls, or background tasks inside serializers. Delegate to domain services instead.

### 3.3 Domain Services (`services/`) — The Business Logic Core
- **When to use**:
  - **All core business logic, domain invariants, mutations, and side effects.**
  - Atomic multi-model transactions (`@transaction.atomic`).
  - Dispatching background tasks (e.g., Huey or Celery jobs).
  - Interacting with third-party APIs (Stripe, Twilio, AWS, external microservices).
  - Complex validations that depend on multiple models, external services, or cross-domain state.
- **Service Invariants**:
  - Services must be decoupled from the HTTP transport layer: **never pass `request` objects into service functions**.
  - Pass explicit arguments (primitives, domain dataclasses, or model instances).
  - This ensures services are 100% reusable across API views, CLI management commands, background workers, and automated tests.

### 3.4 Custom QuerySets & Managers (`models.py` or `managers.py`) — The Data Access Layer
- **When to use Custom QuerySets**:
  - Encapsulating database-level query logic, joins, filters, and aggregations into reusable, chainable methods (e.g., `User.objects.active().verified()`).
  - Performance optimizations: defining `select_related()` and `prefetch_related()` query patterns to eliminate N+1 queries.
- **When to use Custom Managers**:
  - Table-level operations (e.g., `create_user()`, `create_superuser()` on `UserManager`).
  - Overriding `get_queryset()` to enforce global base filters (e.g., soft-delete exclusions, multi-tenant isolation).
- **When NOT to use**:
  - Do not put multi-model mutations, business side-effects, or external API calls in QuerySets or Managers.

### 3.5 Filters (`api/filters.py`) — Query Parameter Mapping
- **When to use**:
  - Mapping HTTP query parameters (e.g., `?status=active&created_after=2026-01-01`) directly to database query filters on listing/collection endpoints using `django-filter`.
  - Text search, ordering, range filtering, and boolean flags.
- **When NOT to use**:
  - Security/authorization filtering (e.g., restricting users to their own data; do this in `get_queryset()` in the view or manager).
  - Mutating state or executing business workflows.

### 3.6 Signals (`signals.py`) — Decoupled Cross-Cutting Hooks
- **When to use**:
  - Purely decoupled, secondary cross-cutting infrastructure hooks (e.g., clearing a cache upon model modification, cleaning up uploaded media files on disk via `post_delete`).
  - Integration with third-party packages that require signal hooks.
- **When to AVOID Signals (Anti-Pattern)**:
  - **Never use signals for core business workflows** (e.g., do not send welcome emails, generate invoices, or charge payments in `post_save` signals).
  - *Why*: Signals obscure execution control flow, trigger unpredictably during bulk updates, migrations, and test fixture setup, and can fail silently or fire multiple times outside transaction boundaries. Handle workflows explicitly in domain services.

---

## 4. Testing Conventions & Best Practices

All tests are executed with `pytest` using `pytest-django`.

### Test Execution
```bash
uv run pytest
```

### Test Standards
- **Test File Naming & Organization**:
  - Always locate tests in an app-level `tests/` package (e.g., `accounts/tests/`) with an `__init__.py`. Never create monolithic `tests.py` files.
  - Always prefix test files with `test_` for automatic `pytest` discovery:
    - Model tests: `test_models.py` (or `test_models_<model_name>.py` for large domains)
    - Service layer tests: `test_services.py` (or `test_<service_name>_service.py`)
    - API & serializer tests: `test_api.py` (or `test_views.py`, `test_serializers.py`)
    - Background task tests: `test_tasks.py`
    - Multi-step integration flows: `test_integration_<flow_name>.py`
  - Avoid suffixes like `models_test.py` or generic names like `test.py` or `tests.py`.
- **Behavior-Driven Naming**: Name test functions using `test_<action>_<expected_outcome>_<condition>`.
  - *Good*: `test_create_user_succeeds_with_valid_credentials`
  - *Good*: `test_create_user_raises_value_error_when_email_missing`
  - *Good*: `test_update_user_modifies_specified_fields`
  - *Avoid*: `test_create_user`, `test_user`, `test_fail`
- **Single Conceptual Assertion**: Each test should verify a single behavior or scenario. Split multi-assertion checks across focused test cases.
- **Test Data with Factory Boy**:
  - Use factories defined in `factories.py` (e.g. `UserFactory`, `SuperUserFactory`).
  - When creating multiple test instances, assign distinct emails or unique keys to prevent `django_get_or_create` collisions.
- **Fast & Isolated**:
  - `config/settings/test.py` uses in-memory SQLite and `MD5PasswordHasher` for maximum execution speed.
  - Do not introduce network calls, sleep calls, or unmocked external I/O into unit tests.

---

## 5. Clean Code & Commenting Guidelines (Uncle Bob)

When writing or refactoring code:

- **Express Intent Through Code**: Make variable, function, and class names descriptive. If the code is self-explanatory, do not add redundant comments.
- **Eliminate Noise Comments**: Avoid section banners and restatements of code:
  - *Avoid*: `# Storage` above `STORAGES = ...`
  - *Avoid*: `# Email Configuration` above `EMAIL_BACKEND = ...`
  - *Avoid*: `# In-memory SQLite database` above `ENGINE: ...sqlite3`
- **Explain Intent ("Why", Not "What")**:
  - Comments should explain non-obvious design decisions, business trade-offs, or workarounds.
  - Example: `# Use a faster hasher to speed up tests`
  - Example: `# Keep sent emails in memory so tests can inspect them without sending real emails`
- **Warn of Consequences**: Add comments when a change could cause security vulnerabilities, data loss, or subtle side effects.

---

## 6. Database Migrations

- Always generate migrations after model changes:
  ```bash
  uv run python manage.py makemigrations
  ```
- Always inspect generated migration files before committing.
- Ensure migrations are reversible whenever possible. Never delete or rename fields in a way that breaks zero-downtime rolling deployments.

---

## 7. Pre-Commit Verification Checklist

Before finishing any task or committing changes, run the following verification checklist:

1. **Run Pre-Commit Hooks**:
   ```bash
   uv run pre-commit run --all-files
   ```
   (This runs `ruff`, formatting, trailing-whitespace, and security checks across the entire repo).

2. **Run Migrations Check**:
   ```bash
   uv run python manage.py makemigrations --check --dry-run
   ```

3. **Execute Test Suite**:
   ```bash
   uv run pytest
   ```
Ensure 100% test pass rate with zero unexpected regressions.
