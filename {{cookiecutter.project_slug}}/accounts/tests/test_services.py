"""
Tests for accounts domain services.
"""
import pytest

from accounts.factories import UserFactory
from accounts.services import UserService


@pytest.mark.django_db
class TestUserService:
    """Tests for UserService domain operations."""

    def test_create_user_persists_user_with_hashed_password(self):
        """Test UserService.create_user persists user with hashed password."""
        user = UserService.create_user(
            email="[email protected]",
            password="securepassword123",
            first_name="Alice",
            last_name="Smith",
        )
        assert user.email == "[email protected]"
        assert user.first_name == "Alice"
        assert user.check_password("securepassword123")

    def test_update_user_modifies_specified_fields(self):
        """Test that UserService.update_user updates and saves specified fields."""
        user = UserFactory(first_name="Old", last_name="Name")
        updated = UserService.update_user(
            user, first_name="New", last_name="Updated"
        )
        assert updated.first_name == "New"
        assert updated.last_name == "Updated"

    def test_change_password_updates_user_password_hash(self):
        """Test UserService.change_password updates user password hash."""
        user = UserFactory(password="oldpass123")
        UserService.change_password(user, "newpass456")
        assert user.check_password("newpass456")
        assert not user.check_password("oldpass123")

