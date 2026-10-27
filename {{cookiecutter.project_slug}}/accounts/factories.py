"""
Model factories for accounts app testing.
"""
import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for standard User model instances."""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create a user with a properly hashed password."""
        password = kwargs.pop("password", "testpass123")
        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save(update_fields=["password"])
        return user


class SuperUserFactory(UserFactory):
    """Factory for superuser instances."""

    is_staff = True
    is_superuser = True
