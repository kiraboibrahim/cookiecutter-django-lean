"""
Production settings for {{ cookiecutter.project_name }}.
"""

from .base import *  # noqa: F403
from .base import BASE_DIR, DATABASES, config

DEBUG = False

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = [
    host.strip()
    for host in config("ALLOWED_HOSTS").split(",")
    if host.strip()
]

{%- if cookiecutter.use_rest_framework == "yes" %}
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config("CORS_ALLOWED_ORIGINS", default="").split(",")
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config("CSRF_TRUSTED_ORIGINS", default="").split(",")
    if origin.strip()
]
{%- endif %}

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
SERVER_EMAIL = config("SERVER_EMAIL", default=EMAIL_HOST_USER)
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=15, cast=int)

USE_S3 = config("USE_S3", default=False, cast=bool)
if USE_S3:
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_SIGNATURE_VERSION = "s3v4"

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

{%- if cookiecutter.use_huey == "yes" %}
HUEY_USE_REDIS = config("HUEY_USE_REDIS", default=False, cast=bool)
if HUEY_USE_REDIS:
    HUEY = {
        "huey_class": "huey.PriorityRedisHuey",
        "name": "{{ cookiecutter.project_slug }}_tasks",
        "url": config("REDIS_URL", default="redis://redis:6379/0"),
        "results": True,
        "store_none": False,
        "immediate": False,
        "utc": True,
        "consumer": {
            "workers": 4,
            "worker_type": "thread",
        },
    }
else:
    HUEY = {
        "huey_class": "huey.SqliteHuey",
        "name": "{{ cookiecutter.project_slug }}_tasks",
        "results": True,
        "store_none": False,
        "immediate": False,
        "utc": True,
        "filename": BASE_DIR / "data" / "huey.sqlite3",
        "consumer": {
            "workers": 4,
            "worker_type": "thread",
        },
    }
{%- endif %}
