"""
Pre-generation hook for Django project template.

This hook validates user inputs before the cookiecutter template generates the project.
It ensures that:
- The project slug is a valid Python module name
- The Python version meets minimum requirements
- At least one app is selected (or warns if none are)

Exit codes:
    0: Validation passed
    1: Validation failed (project generation aborted)
"""
import re
import sys
from typing import Final

MODULE_REGEX: Final[str] = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

MIN_PYTHON_MAJOR: Final[int] = 3
MIN_PYTHON_MINOR: Final[int] = 12


def validate_project_slug(slug: str) -> None:
    """
    Validate that the project slug is a valid Python module name.
    
    Args:
        slug: The project slug to validate
        
    Raises:
        SystemExit: If the slug is invalid (exit code 1)
    """
    if not re.match(MODULE_REGEX, slug):
        print(
            f"ERROR: '{slug}' is not a valid Python module name!"
            "\n"
            "\nModule names must:"
            "\n  - Start with a letter or underscore"
            "\n  - Contain only letters, numbers, and underscores"
            "\n  - Not contain spaces or hyphens"
            "\n"
            "\nExamples of valid names:"
            "\n  - my_project"
            "\n  - MyProject"
            "\n  - _private_project"
            "\n  - project2"
        )
        sys.exit(1)


def validate_python_version(version: str) -> None:
    """
    Validate that the Python version meets minimum requirements.
    
    Args:
        version: Python version string in format "X.Y" (e.g., "3.12")
        
    Raises:
        SystemExit: If the version is invalid or below minimum (exit code 1)
    """
    try:
        major, minor = map(int, version.split("."))
    except ValueError:
        print(
            f"ERROR: Invalid Python version format: '{version}'"
            "\n"
            "\nExpected format: X.Y (e.g., 3.12)"
            "\n"
            "\nValid examples:"
            "\n  - 3.12"
            "\n  - 3.13"
        )
        sys.exit(1)
    
    if major < MIN_PYTHON_MAJOR or (major == MIN_PYTHON_MAJOR and minor < MIN_PYTHON_MINOR):
        print(
            f"ERROR: Python version {version} is not supported!"
            "\n"
            f"\nThis template requires Python {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR} or higher."
            "\n"
            "\nRecommended versions:"
            "\n  - 3.12 (stable)"
            "\n  - 3.13 (latest)"
        )
        sys.exit(1)


def check_app_selection(apps: list[str]) -> None:
    """
    Warn if no apps are selected (non-fatal check).
    
    Args:
        apps: List of app selection values ("yes" or "no")
    """
    if not any(app == "yes" for app in apps):
        print(
            "⚠ WARNING: Accounts app not selected."
            "\n"
            "\nThe project will only have the config module."
            "\nYou can add apps later with:"
            "\n  python manage.py startapp <app_name>"
            "\n"
        )


def main() -> None:
    """Run all validation checks on cookiecutter variables."""
    project_slug: str = "{{ cookiecutter.project_slug }}"
    python_version: str = "{{ cookiecutter.python_version }}"
    
    validate_project_slug(project_slug)
    validate_python_version(python_version)
    
    apps_selected: list[str] = [
        "{{ cookiecutter.include_accounts_app }}",
        # Add more apps here as template expands
    ]
    check_app_selection(apps_selected)
    
    print("✓ Pre-generation validation passed!")


if __name__ == "__main__":
    main()