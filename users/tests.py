from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class AuthRegistrationTests(APITestCase):

    def test_register_valid_user(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "role": "basic",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["role"], "basic")

    def test_register_password_mismatch(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
            "password_confirm": "differentpass",
            "role": "basic",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST])

    def test_register_invalid_role(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "role": "admin",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST])

    def test_register_duplicate_username(self):
        User.objects.create_user(username="existing", password="pass12345678")
        data = {
            "username": "existing",
            "email": "new@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "role": "basic",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST])


class AuthLoginTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser", password="testpass123", role="basic"
        )

    def test_login_valid(self):
        data = {"username": "loginuser", "password": "testpass123"}
        response = self.client.post("/api/auth/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_password(self):
        data = {"username": "loginuser", "password": "wrongpassword"}
        response = self.client.post("/api/auth/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeEndpointTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="meuser", password="testpass123", role="pro"
        )

    def test_me_unauthenticated(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "meuser")
        self.assertEqual(response.data["role"], "pro")
