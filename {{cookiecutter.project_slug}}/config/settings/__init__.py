"""
Settings package initialization for {{ cookiecutter.project_name }}.
Dynamically resolves environment configuration with backward compatibility
for `config.settings` imports and DJANGO_SETTINGS_MODULE configurations.
"""

import os
import sys

IS_TESTING = (
    "test" in sys.argv
    or any("pytest" in arg for arg in sys.argv)
    or "pytest" in sys.modules
    or bool(os.environ.get("PYTEST_CURRENT_TEST"))
)
DJANGO_ENV = os.environ.get("DJANGO_ENV") or os.environ.get("ENVIRONMENT", "")

if IS_TESTING:
    from .test import *  # noqa: F403
elif DJANGO_ENV.lower() in ("production", "prod"):
    from .prod import *  # noqa: F403
else:
    from decouple import config

    if config("DEBUG", default=True, cast=bool):
        from .local import *  # noqa: F403
    else:
        from .prod import *  # noqa: F403
