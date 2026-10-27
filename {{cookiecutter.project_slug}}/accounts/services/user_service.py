"""
Domain services for user management and business logic.
"""
from typing import Any
from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:
    """Service handling user domain operations."""

    @staticmethod
    def create_user(
        email: str, password: str | None = None, **extra_fields: Any
    ) -> Any:
        """Create and return a new user."""
        return User.objects.create_user(
            email=email, password=password, **extra_fields
        )

    @staticmethod
    def update_user(user: Any, **fields: Any) -> Any:
        """Update user fields and save."""
        for field, value in fields.items():
            if hasattr(user, field):
                setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def change_password(user: Any, new_password: str) -> None:
        """Change user password securely."""
        user.set_password(new_password)
        user.save(update_fields=["password"])
