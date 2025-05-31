from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import Business, Service, TemporaryCode, VerificationCode
from core.utils import generate_secure_six_digits, hash256

User = get_user_model()


class LoginViewsetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+251911223344",
            password="testpass",
            first_name="Test",
            user_type="user",
        )

        self.user.is_phone_verified = True
        self.user.save()

    def test_login_successful(self):
        url = reverse("login-list")
        data = {"phone_number": "+251911223344", "password": "testpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RegisterViewsetTests(APITestCase):
    def test_register_user(self):
        url = reverse("register-list")
        data = {
            "phone_number": "+251912345678",
            "first_name": "Test",
            "password": "securePassword123",
            "user_type": "user",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(
                phone_number=User.normalize_phone_number("+251912345678")
            ).exists()
        )


class UsersViewsetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="912345678",
            password="testpass",
            is_active=True,
            first_name="testUser",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_users(self):
        url = reverse("users-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user(self):
        url = reverse("users-detail", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BusinessViewsetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="912345678", password="testUser", first_name="TestUSer"
        )

        self.client.force_authenticate(user=self.user)
        self.business = Business.objects.create(
            name="My Shop",
            owner=self.user,
            contact_phone=self.user.phone_number,
            contact_email="example@test.com",
            is_verified=True,
            is_active=True,
        )

    def test_list_businesses(self):
        url = reverse("business-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_business(self):
        url = reverse("business-detail", args=[self.business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# class BusinessServiceViewsetTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username="serviceuser", password="pass")
#         self.client.force_authenticate(user=self.user)
#         self.service = Service.objects.create(name="Delivery", is_active=True)

#     def test_list_services(self):
#         url = reverse("business-services-list")
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_retrieve_service(self):
#         url = reverse("business-services-detail", args=[self.service.id])
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="912345678",
            password="testpass123",
            first_name="Test",
            user_type="user",
            is_phone_verified=True,
        )
        self.client = APIClient()

    def test_request_password_reset(self):
        """Test requesting a password reset code"""
        url = reverse("password-reset-request-list")
        data = {"phone_number": "912345678"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("detail", response.data)

        # Verify verification code was created
        self.assertTrue(
            VerificationCode.objects.filter(
                user=self.user, code_type=1, is_used=False
            ).exists()
        )

    def test_request_password_reset_invalid_phone(self):
        """Test requesting password reset with invalid phone number"""
        url = reverse("password-reset-request-list")
        data = {"phone_number": "999999999"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)

    def test_confirm_password_reset(self):
        """Test confirming password reset with valid code"""
        # Create a verification code
        token = generate_secure_six_digits()
        verification_code = VerificationCode.objects.create(
            user=self.user,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=5),
            code_type=1,
        )
        TemporaryCode.objects.create(code=token, phone_number=self.user.phone_number)

        url = reverse("password-reset-confirm-list")
        data = {
            "code": token,
            "phone_number": str(self.user.phone_number),
            "new_password": "newpass123",
        }
        response = self.client.post(url, data)

        print(response.data)  # Debugging line to see response data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("detail", response.data)

        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

        # Verify verification code was marked as used
        verification_code.refresh_from_db()
        self.assertTrue(verification_code.is_used)

    def test_confirm_password_reset_invalid_code(self):
        """Test confirming password reset with invalid code"""
        url = reverse("password-reset-confirm-list")
        data = {
            "code": "123456",
            "user_id": str(self.user.id),
            "new_password": "newpass123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_password_reset_invalid_password(self):
        """Test confirming password reset with invalid new password"""
        # Create a verification code
        token = generate_secure_six_digits()
        VerificationCode.objects.create(
            user=self.user,
            token=hash256(token),
            expires_at=timezone.now() + timedelta(minutes=5),
            code_type=1,
        )
        TemporaryCode.objects.create(code=token, phone_number=self.user.phone_number)

        url = reverse("password-reset-confirm-list")
        data = {
            "code": token,
            "phone_number": str(self.user.phone_number),
            "new_password": "123",  # Too short password
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
