"""
Base Django settings for {{ cookiecutter.project_name }} project.
Shared across all environments (local, production, testing).
"""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import config
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file with interpolation support
load_dotenv(BASE_DIR / ".env")

# Ensure data directory exists
(BASE_DIR / "data").mkdir(exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="django-insecure-default-key-for-development")

# Application definition
DJANGO_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
{%- if cookiecutter.use_rest_framework == "yes" %}
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "dj_rest_auth",
    "drf_yasg",
{%- endif %}
    "guardian",
{%- if cookiecutter.use_huey == "yes" %}
    "huey.contrib.djhuey",
{%- endif %}
]

LOCAL_APPS = [
    "config",
{%- if cookiecutter.include_accounts_app == "yes" %}
    "accounts",
{%- endif %}
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
{%- if cookiecutter.use_rest_framework == "yes" %}
    "corsheaders.middleware.CorsMiddleware",
{%- endif %}
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database defaults
DEFAULT_DATABASE_URL = "sqlite:///" + str(BASE_DIR / "data" / "db.sqlite3")
DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL", default=DEFAULT_DATABASE_URL)
    )
}
if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    DATABASES["default"]["NAME"] = BASE_DIR / "data" / "db.sqlite3"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Auth backends
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
)

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "{{ cookiecutter.timezone }}"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

{%- if cookiecutter.include_accounts_app == "yes" %}
AUTH_USER_MODEL = "accounts.User"
{%- endif %}

{%- if cookiecutter.use_rest_framework == "yes" %}
# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "access",
    "JWT_AUTH_REFRESH_COOKIE": "refresh",
    "JWT_AUTH_HTTPONLY": False,
    "LOGIN_SERIALIZER": "accounts.api.serializers.LoginSerializer",
    "USER_DETAILS_SERIALIZER": "accounts.api.serializers.UserSerializer",
    "JWT_AUTH_SAMESITE": config("JWT_AUTH_SAMESITE", default="Lax"),
    "JWT_AUTH_SECURE": config("JWT_AUTH_SECURE", default=False, cast=bool),
}
{%- endif %}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "daphne.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
