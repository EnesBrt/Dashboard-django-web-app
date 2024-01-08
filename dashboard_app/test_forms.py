import pytest
from django.test import TestCase
from . import views
from dashboard_app.forms import CustomUserCreationForm
from dashboard_app.forms import LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


# Create your tests here

import pytest
from django.contrib.auth.models import User
from dashboard_app.forms import (
    CustomUserCreationForm,
)


@pytest.mark.django_db
class TestCustomUserCreationForm:
    def test_valid_data_creates_user(self):
        form = CustomUserCreationForm(
            data={
                "username": "alex",
                "email": "alex@example.com",
                "password": "Testpassword123",
            }
        )
        assert form.is_valid()
        user = form.save()
        assert User.objects.filter(username="alex").exists()

    def test_invalid_email_raises_error(self):
        User.objects.create_user(
            username="existinguser",
            email="test@example.com",
            password="Testpassword123",
        )
        form = CustomUserCreationForm(
            data={
                "username": "newuser",
                "email": "test@example.com",
                "password": "Testpassword123",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors

    def test_invalid_password_raises_error(self):
        form = CustomUserCreationForm(
            data={
                "username": "alex",
                "email": "alex@example.com",
                "password": "password",
            }
        )
        assert not form.is_valid()
        assert "password" in form.errors


@pytest.mark.django_db
class TestLoginForm:
    @pytest.fixture(autouse=True)
    def setup_user(self):
        User.objects.create_user(username="alex", password="Testpassword123")

    def test_user_authentication_with_valid_credentials(self):
        form = LoginForm(data={"username": "alex", "password": "Testpassword123"})
        assert form.is_valid()
        user = authenticate(username="alex", password="Testpassword123")
        assert user is not None

    def test_user_authentication_with_invalid_password(self):
        form = LoginForm(data={"username": "alex", "password": "wrongpassword"})
        assert form.is_valid()  # Le formulaire doit être techniquement valide
        user = authenticate(username="alex", password="wrongpassword")
        assert user is None
