{%- if cookiecutter.use_rest_framework == "yes" %}
"""
Tests for accounts API endpoints and serializers.
"""
import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.api.serializers import UserSerializer
from accounts.api.views import UserProfileView
from accounts.factories import UserFactory


@pytest.mark.django_db
class TestAccountsAPI:
    """Tests for accounts serializers and views."""

    def test_user_serializer_serializes_expected_fields(self):
        """Test that UserSerializer includes email, first_name, and last_name fields."""
        user = UserFactory(
            email="[email protected]", first_name="John", last_name="Doe"
        )
        serializer = UserSerializer(instance=user)
        assert serializer.data["email"] == "[email protected]"
        assert serializer.data["first_name"] == "John"
        assert serializer.data["last_name"] == "Doe"

    def test_user_profile_view_returns_ok_for_authenticated_user(self):
        """Test GET /api/accounts/profile/ returns 200 when authenticated."""
        user = UserFactory(
            email="[email protected]", first_name="John", last_name="Doe"
        )
        factory = APIRequestFactory()
        request = factory.get("/api/accounts/profile/")
        force_authenticate(request, user=user)

        view = UserProfileView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert response.data["email"] == "[email protected]"

    def test_user_profile_view_returns_unauthorized_for_anonymous_request(self):
        """Test GET /api/accounts/profile/ returns 401 when unauthenticated."""
        factory = APIRequestFactory()
        request = factory.get("/api/accounts/profile/")

        view = UserProfileView.as_view()
        response = view(request)
        assert response.status_code == 401
{%- endif %}

