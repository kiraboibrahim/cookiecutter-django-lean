"""
Local / Development settings for {{ cookiecutter.project_name }}.
"""

from .base import *  # noqa: F403
from .base import BASE_DIR, DATABASES, config

DEBUG = True

ALLOWED_HOSTS = [
    host.strip()
    for host in config(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1,0.0.0.0",
    ).split(",")
    if host.strip()
]

{%- if cookiecutter.use_rest_framework == "yes" %}
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
{%- endif %}

{%- if cookiecutter.use_mailpit == "yes" %}
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=1025, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)
{%- else %}
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=1025, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)
{%- endif %}
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@localhost")
SERVER_EMAIL = config("SERVER_EMAIL", default="server@localhost")
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=15, cast=int)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

{%- if cookiecutter.use_huey == "yes" %}
HUEY = {
    "huey_class": "huey.SqliteHuey",
    "name": "{{ cookiecutter.project_slug }}_tasks",
    "results": True,
    "store_none": False,
    "immediate": False,
    "utc": True,
    "filename": BASE_DIR / "data" / "huey.sqlite3",
    "consumer": {
        "workers": 2,
        "worker_type": "thread",
    },
}
{%- endif %}

(BASE_DIR / "data").mkdir(exist_ok=True)
