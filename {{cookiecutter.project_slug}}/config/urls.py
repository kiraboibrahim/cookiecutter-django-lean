"""
URL configuration for {{ cookiecutter.project_name }} project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path

{%- if cookiecutter.use_rest_framework == "yes" %}
from django.urls import include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="{{ cookiecutter.project_name }} API",
        default_version="v1",
        description="{{ cookiecutter.project_description }}",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
{%- endif %}


def health_check(request):
    return HttpResponse("OK")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
{%- if cookiecutter.use_rest_framework == "yes" %}
    path("api/auth/", include("dj_rest_auth.urls")),
{%- if cookiecutter.include_accounts_app == "yes" %}
    path("api/accounts/", include("accounts.urls")),
{%- endif %}
    path(
        "api/swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
{%- endif %}
]
