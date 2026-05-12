"""Тесты регистрации и входа (Token)."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success_returns_201_and_token(self):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "ComplexPass123!",
            "password_confirm": "ComplexPass123!",
            "display_name": "Новый",
        }
        response = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "newuser")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username_returns_400(self):
        User.objects.create_user("taken", "t1@example.com", "ComplexPass123!")
        payload = {
            "username": "taken",
            "email": "other@example.com",
            "password": "ComplexPass123!",
            "password_confirm": "ComplexPass123!",
        }
        response = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", str(response.data).lower() or response.data)

    def test_login_success_returns_200_and_token(self):
        User.objects.create_user("bob", "bob@example.com", "CorrectPass123!")
        response = self.client.post(
            "/api/auth/login/",
            {"username": "bob", "password": "CorrectPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "bob")

    def test_login_wrong_password_returns_400(self):
        """
        Неверный пароль обрабатывается LoginSerializer: ValidationError → 400.
        (Не 401: не используется HTTPUnauthorized от DRF для этого кейса.)
        """
        User.objects.create_user("carol", "carol@example.com", "RightPass123!")
        response = self.client.post(
            "/api/auth/login/",
            {"username": "carol", "password": "WrongPassword999!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
