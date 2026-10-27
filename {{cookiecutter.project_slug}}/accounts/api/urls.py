"""
Routing configuration for accounts API endpoints.
"""
from django.urls import path

from accounts.api.views import UserProfileView

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]
