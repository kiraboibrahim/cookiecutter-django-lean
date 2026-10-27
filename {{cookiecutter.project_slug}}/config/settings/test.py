"""
Test settings for {{ cookiecutter.project_name }}.
Optimized for fast, isolated tests.
"""

from .base import *  # noqa: F403

SECRET_KEY = "django-insecure-test-key-for-isolated-pytest"  # nosec B105

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Use a faster hasher to speed up tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Keep sent emails in memory so tests can inspect them without sending real emails
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

{%- if cookiecutter.use_huey == "yes" %}
# Run tasks immediately so tests don't need a separate background worker
HUEY = {
    "huey_class": "huey.SqliteHuey",
    "name": "{{ cookiecutter.project_slug }}_test",
    "immediate": True,
    "results": True,
    "store_none": False,
    "utc": True,
}
{%- endif %}


