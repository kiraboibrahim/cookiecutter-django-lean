# AI Agent Guidelines for Cookie Cutter Django Lean

This document provides operational rules, architectural invariants, and verification standards for AI coding agents maintaining this **Cookiecutter Django Lean** template repository.

---

## 1. Operational Boundaries

| Tier | Directives |
| :--- | :--- |
| **Always** | Preserve Jinja template conditionals (`{% if ... %}`); test end-to-end generation before declaring done; mirror changes across `cookiecutter.json`, template files, and `hooks/post_gen_project.py`. |
| **Ask First** | Adding/removing template configuration choices in `cookiecutter.json`; altering supported Python/Django versions; removing bundled architectural layers. |
| **Never** | Hardcode project values into `{{cookiecutter.project_slug}}/`; touch or commit secrets; run `git commit` or `git push` unless explicitly asked. |

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
- **Service Layer First**: Business logic must reside strictly in `services/` (e.g. `user_service.py`), keeping API views, serializers, and models thin.
- **No `request` in services**: Never pass the HTTP `request` object into service layer functions.
- **Settings Hierarchy**: Environment settings are split under `config/settings/` (`base.py`, `local.py`, `prod.py`, `test.py`, `__init__.py`). Resolve via `DJANGO_ENV` and `python-decouple`.
- **User Model Invariant**: Use `get_user_model()` in code and `settings.AUTH_USER_MODEL` in model foreign keys. Never import the User model directly from app models across apps.
- **Signals**: Never use signals for business logic (emails, payments, user creation). Reserved strictly for decoupled infrastructure hooks (cache clearing, file deletion on `post_delete`).

---

## 3. Testing Conventions

- **File Naming & Location**: App tests live in `tests/` with `__init__.py`, prefixed with `test_` (`test_models.py`, `test_services.py`, `test_api.py`).
- **Naming Pattern**: Behavior-driven naming: `test_<action>_<expected_outcome>_<condition>`.
- **Assertions**: Multiple `assert` statements are encouraged when verifying facets of a single behavior.
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
