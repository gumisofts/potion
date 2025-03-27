from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import EmailConfirmationToken

User = get_user_model()


class UsersAPIViewsTests(APITestCase):
    pass

    # def test_user_information_api_view_requires_authentication(self):
    #     url = reverse("users-list")
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 401)

    # def test_send_email_confirmation_api_view_requires_authentication(self):
    #     url = reverse("users:send_email_confirmation_api_view")
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 401)

    # def test_send_email_confirmation_api_creates_token(self):
    #     user = User.objects.create(
    #         first_name="new",
    #         last_name="user2",
    #         password="admin123j",
    #         email="newuser2@example.com",
    #         phone_number="911223346",
    #     )
    #     url = reverse("users:send_email_confirmation_api_view")
    #     self.client.force_authenticate(user=user)
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 201)
    #     token = EmailConfirmationToken.objects.filter(user=user).first()
    #     self.assertIsNotNone(token)