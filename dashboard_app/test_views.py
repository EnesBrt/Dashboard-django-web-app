import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from . import views
from django.urls import reverse
from django.test import Client


@pytest.mark.django_db
class TestViews:
    def setup_method(self):
        self.client = Client()
        User.objects.create_user(username="alex", password="Testpassword123")

    def test_signup_view(self):
        url = reverse("signup")  # Remplacez par le nom d'URL réel
        response = self.client.get(url)
        assert response.status_code == 200
        assert "signup.html" in [t.name for t in response.templates]

        # Test de soumission de formulaire
        response = self.client.post(
            url,
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "Newpassword123",
            },
        )
        assert response.status_code == 302  # Redirection

    def test_login_view(self):
        url = reverse("login")
        response = self.client.get(url)
        assert response.status_code == 200
        assert "login.html" in [t.name for t in response.templates]

        # Test de connexion réussie
        response = self.client.post(
            url, {"username": "alex", "password": "Testpassword123"}
        )
        assert response.status_code == 302  # Redirection

        # Test de connexion échouée
        response = self.client.post(url, {"username": "qlex", "password": "wrong"})
        assert response.status_code == 200  # Pas de redirection
        assert "login.html" in [
            t.name for t in response.templates
        ]  # Rendu à nouveau du formulaire de connexion

    def test_logout_view(self):
        url = reverse("logout")  # Remplacez par le nom d'URL réel
        response = self.client.get(url)
        assert response.status_code == 200
        assert "logout.html" in [t.name for t in response.templates]

    def test_dashboard_view(self):
        url = reverse("dashboard")  # Remplacez par le nom d'URL réel
        response = self.client.get(url)
        assert response.status_code == 200
        assert "dashboard.html" in [t.name for t in response.templates]
