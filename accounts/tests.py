from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Business, Service

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


# class VerificationCodeViewsetTests(APITestCase):
#     def test_create_verification_code(self):
#         url = reverse("users-confirm-code-list")
#         data = {"email": "test@example.com"}
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# class VerificationCodeResendViewsetTests(APITestCase):
#     def test_resend_verification_code(self):
#         url = reverse("users-resend-code-list")
#         data = {"email": "test@example.com"}
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)


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
