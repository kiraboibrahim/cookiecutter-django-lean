"""
Architectural invariant tests enforcing clean layer separation and package layout.
"""

import ast
from pathlib import Path

from django.conf import settings

FORBIDDEN_APP_ROOT_FILES = {
    "views.py",
    "serializers.py",
    "filters.py",
    "permissions.py",
    "viewsets.py",
    "pagination.py",
    "schemas.py",
    "services.py",  # Must be a services/ package, not a flat file
}


def _get_local_app_paths() -> list[Path]:
    """Retrieve paths of all first-party apps located within BASE_DIR."""
    base_dir = Path(settings.BASE_DIR)
    app_paths = []
    for app_config in settings.INSTALLED_APPS:
        app_name = app_config.split(".")[0]
        app_path = base_dir / app_name
        if (
            app_path.is_dir()
            and (app_path / "apps.py").exists()
            and app_path not in app_paths
        ):
            app_paths.append(app_path)
    return app_paths


def test_no_flat_transport_files_at_app_roots():
    """Ensure HTTP transport, permissions, filters, and flat services do not exist at app roots."""
    for app_path in _get_local_app_paths():
        for forbidden in FORBIDDEN_APP_ROOT_FILES:
            file_path = app_path / forbidden
            assert not file_path.exists(), (
                f"Architecture violation: '{forbidden}' found in app root '{app_path.name}/'. "
                f"Transport logic belongs in '{app_path.name}/api/', services in '{app_path.name}/services/'."
            )


def test_app_root_urls_do_not_bind_views_directly():
    """Root <app>/urls.py may only delegate to api/urls.py, never bind views directly."""
    for app_path in _get_local_app_paths():
        urls_file = app_path / "urls.py"
        if urls_file.exists():
            content = urls_file.read_text()
            assert "as_view" not in content, (
                f"Architecture violation in '{app_path.name}/urls.py': "
                f"Direct view binding is forbidden. Route endpoints inside '{app_path.name}/api/urls.py'."
            )


def test_dependency_flow_invariants():
    """
    Statically enforce one-way dependency flow:
    - models.py must not import from services or api
    - services/ must not import from api or transport request objects
    """
    for app_path in _get_local_app_paths():
        # Check models.py
        models_file = app_path / "models.py"
        if models_file.exists():
            tree = ast.parse(models_file.read_text(), filename=str(models_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert (
                        ".services" not in node.module
                        and not node.module.endswith("services")
                    ), f"Architecture violation in '{models_file}': models must never import from services."
                    assert (
                        ".api" not in node.module and not node.module.endswith("api")
                    ), f"Architecture violation in '{models_file}': models must never import from api."
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        assert (
                            "services" not in alias.name.split(".")
                        ), f"Architecture violation in '{models_file}': models must never import from services."
                        assert (
                            "api" not in alias.name.split(".")
                        ), f"Architecture violation in '{models_file}': models must never import from api."

        # Check services/ package
        services_dir = app_path / "services"
        if services_dir.is_dir():
            for py_file in services_dir.glob("*.py"):
                tree = ast.parse(py_file.read_text(), filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        assert (
                            ".api" not in node.module
                            and not node.module.endswith("api")
                        ), f"Architecture violation in '{py_file}': services must never import from api."
                        assert (
                            "rest_framework.request" not in node.module
                        ), f"Architecture violation in '{py_file}': services must never import Request objects."
                        if node.module == "django.http":
                            for alias in node.names:
                                assert (
                                    "HttpRequest" not in alias.name
                                ), f"Architecture violation in '{py_file}': services must never import HttpRequest."
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            assert (
                                "api" in alias.name.split(".") is False
                            ), f"Architecture violation in '{py_file}': services must never import from api."
                            assert (
                                alias.name != "rest_framework.request"
                            ), f"Architecture violation in '{py_file}': services must never import Request objects."
