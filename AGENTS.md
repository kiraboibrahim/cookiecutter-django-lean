# AI Agent Guidelines for Cookie Cutter Django Lean

This document provides operational principles, architectural rules, and development conventions for AI coding agents working on the **Cookie Cutter Django Lean** template repository.

---

## 1. Repository Structure & Roles

This repository is a **Cookiecutter template** for generating lean, production-ready Django applications:

```
Cookie Cutter Django Lean/
├── cookiecutter.json               # Template variables and default configuration
├── hooks/
│   ├── pre_gen_project.py          # Pre-generation validations (slug, python, etc.)
│   └── post_gen_project.py         # Post-generation setup (git init, uv sync, .env)
├── {{cookiecutter.project_slug}}/  # Django project template root
│   ├── config/
│   │   ├── settings/               # Modular settings (base, local, prod, test)
│   │   └── urls.py                 # Root URL configuration
│   ├── accounts/                   # Modular accounts app (optional)
│   │   ├── models.py
│   │   ├── api/                    # Dedicated REST API module
│   │   ├── services/               # Domain business logic layer
│   │   ├── factories.py            # Test factories
│   │   └── tests/                  # Behavior-driven unit tests
│   ├── pyproject.toml              # Dependencies and tool configurations
│   ├── AGENTS.md                   # Agent guidelines bundled into generated projects
│   └── README.md                   # Generated project documentation
└── README.md                       # Template documentation
```

---

## 2. Core Operational Directives

### 2.1 Preserving Jinja Template Syntax
- Files inside `{{cookiecutter.project_slug}}/` contain Jinja template syntax (e.g., `{% if cookiecutter.use_rest_framework == "yes" %}`, `{{ cookiecutter.project_name }}`).
- **Always preserve conditional blocks** when editing template files. Never remove feature conditionals unless explicitly requested.
- When adding new dependencies or features, remember to update:
  1. `cookiecutter.json` (if configurable)
  2. `{{cookiecutter.project_slug}}/pyproject.toml`
  3. `hooks/post_gen_project.py` (if post-generation commands or environment generation are affected)
  4. Both `README.md` files (root and template)

### 2.2 Testing Template Changes
Whenever changes are made to the template or post-generation hooks, test full generation and test suite execution:

```bash
# Generate a test project in a temporary scratch directory
mkdir -p /tmp/cookiecutter_test
cd /tmp/cookiecutter_test
rm -rf test_proj
uvx cookiecutter "<path_to_template_root>" --no-input project_slug="test_proj"

# Verify that tests pass in the generated project
cd test_proj
uv run pytest -v

# Clean up
cd ..
rm -rf test_proj
```

### 2.3 Development Server Command (`manage.py dev`)
- Generated projects bundle a custom `dev` management command (`config/management/commands/dev.py`) that concurrently runs the Django development server and the Huey worker with auto-restarts.
- This is a long-running foreground process intended for human developers. Agents should **not** invoke it synchronously during verification runs; use `uv run pytest` instead.

---

## 3. Architecture & Code Quality Standards

### 3.1 Django Architecture Invariants
- **Domain Services First**: Business logic must reside in `services/` (e.g. `user_service.py`), keeping API views, serializers, and models thin.
- **Settings Hierarchy**: Environment settings are split under `config/settings/` (`base.py`, `local.py`, `prod.py`, `test.py`, `__init__.py`). Never hardcode secrets in settings; use `python-decouple`.
- **User Model Invariant**: Use `get_user_model()` in code and `settings.AUTH_USER_MODEL` in model foreign keys. Never import the User model directly from app models across apps.

### 3.2 Component Responsibilities & Division of Concerns
- **Views (`api/views.py`)**: Pure HTTP transport layer. Responsible for parsing requests, checking permissions, validating input with serializers, invoking domain services, and returning responses with proper status codes. No direct business logic, external API calls, or email sending.
- **Serializers (`api/serializers.py`)**: Responsible for data conversion to/from JSON and input format validation. No multi-model orchestration, emails, or background task dispatching.
- **Domain Services (`services/`)**: The business logic engine. Responsible for atomic multi-model transactions, external API interactions, background task dispatch, and cross-model validation. Must be decoupled from HTTP `request` objects.
- **Custom QuerySets & Managers (`models.py` / `managers.py`)**: Encapsulate reusable query filters (`.active()`, `.verified()`), annotations, and eager loading (`select_related`, `prefetch_related`) to prevent N+1 queries. Managers handle table-level creation (`create_user`) and global base querysets.
- **Filters (`api/filters.py`)**: Map HTTP query string parameters directly to database lookups on collection endpoints via `django-filter`.
- **Signals (`signals.py`)**: Reserved strictly for decoupled infrastructure hooks (cache invalidation, physical file cleanup on delete). **Never use signals for core business workflows** (emails, invoices, payments); use domain services instead.

### 3.3 Testing Best Practices
- **Test File Naming & Organization**:
  - Always place tests in an app-level `tests/` directory with `__init__.py` (never a single `tests.py`).
  - Always prefix test files with `test_` (`test_models.py`, `test_services.py`, `test_api.py`, `test_tasks.py`).
- **Behavior-Driven Naming**: Use `test_<action>_<expected_outcome>_<condition>` for all test functions.
- **Factory Boy**: Use factories from `factories.py` with unique identifier patterns to avoid `django_get_or_create` deduplication collisions.
- **Test Performance**: Tests run against `config.settings.test` (in-memory SQLite, MD5 hasher) without external network I/O.

### 3.4 Clean Code & Uncle Bob's Comment Guidelines
- Avoid noise/marker comments that merely restate variable names (`# Storage`, `# Email`).
- Use comments strictly to explain non-obvious *intent* ("why") or warn of consequences.
- Write self-explanatory code with clear, descriptive naming.

---

## 4. Verification Checklist Before Completing Tasks

1. Ensure template syntax is valid and uncorrupted.
2. If environment variables were modified, update `.env.example` and verify that `hooks/post_gen_project.py` generates `.env.test` correctly.
3. Generate a project with `uvx cookiecutter . --no-input` and run:
   - `uv run pre-commit run --all-files`
   - `uv run pytest`
4. Ensure all pre-commit hooks and test suites pass with 0 errors.
