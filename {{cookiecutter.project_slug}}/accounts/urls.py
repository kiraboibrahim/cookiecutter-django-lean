"""
Main URL configuration for the accounts app.
"""
from django.urls import include, path

app_name = "accounts"

urlpatterns = [
    path("", include("accounts.api.urls")),
]
