"""
Tests for accounts models.
"""
import pytest
from django.contrib.auth import get_user_model

from accounts.factories import SuperUserFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""

    def test_create_user_succeeds_with_valid_credentials(self):
        """Test creating a regular user via factory."""
        user = UserFactory(email="user@example.com", password="testpass123")
        assert user.email == "user@example.com"
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
        assert user.check_password("testpass123")

    def test_create_superuser_sets_staff_and_superuser_flags(self):
        """Test creating a superuser via factory."""
        user = SuperUserFactory(email="admin@example.com", password="testpass123")
        assert user.email == "admin@example.com"
        assert user.is_active
        assert user.is_staff
        assert user.is_superuser

    def test_user_str_returns_email_address(self):
        """Test User __str__ method returns email."""
        user = UserFactory(email="string@example.com")
        assert str(user) == "string@example.com"

    def test_display_name_returns_full_name_when_names_present(self):
        """Test User display_name property returns full name when names are set."""
        user = UserFactory(
            first_name="Jane", last_name="Doe", email="withname@example.com"
        )
        assert user.display_name == "Jane Doe"

    def test_display_name_falls_back_to_email_when_names_empty(self):
        """Test User display_name property falls back to email when names are empty."""
        user = UserFactory(
            first_name="", last_name="", email="noname@example.com"
        )
        assert user.display_name == "noname@example.com"

    def test_create_user_raises_value_error_when_email_missing(self):
        """Test creating user without email raises ValueError."""
        with pytest.raises(ValueError, match="The Email field must be set"):
            User.objects.create_user(email="", password="testpass123")

