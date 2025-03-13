from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import EmailConfirmationToken

User = get_user_model()


class UsersAPIViewsTests(APITestCase):

    # def test_register_api_view(self):
    #     url = reverse('users:register_api_view')
    #     body = {"first_name": "new","last_name": "user2","username": "newuser2","password": "admin123j","password_confirmation": "admin123j","email": "newuser2@example.com","phone_number": "911223346"}
    #     response = self.client.post(url, body, format='json')
    #     self.assertEquals(response.status_code,201)
    #     user = User.objects.filter(email=body['email']).first()
    #     self.assertIsNotNone(user)
    #     self.assertTrue(user.check_password(body['password']))

    def test_user_information_api_view_requires_authentication(self):
        url = reverse("users:user_information_api_view")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)

    def test_send_email_confirmation_api_view_requires_authentication(self):
        url = reverse("users:send_email_confirmation_api_view")
        response = self.client.post(url)
        self.assertEquals(response.status_code, 401)

    def test_send_email_confirmation_api_creates_token(self):
        user = User.objects.create_user(
            first_name="new",
            last_name="user2",
            username="newuser2",
            password="admin123j",
            email="newuser2@example.com",
            phone_number="911223346",
        )
        url = reverse("users:send_email_confirmation_api_view")
        self.client.force_authenticate(user=user)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 201)
        token = EmailConfirmationToken.objects.filter(user=user).first()
        self.assertIsNotNone(token)
