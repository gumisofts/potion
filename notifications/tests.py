from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from notifications.models import Notification

User = get_user_model()


class NotificationViewsetTest(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            first_name="testuser1", phone_number="912345678", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            first_name="testuser2", phone_number="987654321", password="testpass123"
        )

        # Create test group
        self.group = Group.objects.create(name="test_group")
        self.user1.groups.add(self.group)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.url = reverse("notifications-list")

        # Create test notifications
        # Broadcast notification for group
        self.group_notification = Notification.objects.create(
            title="Group Notification",
            content="This is a notification for the test group",
            notification_type="broadcast",
            delivery_method="inApp",
        )
        self.group_notification.groups.add(self.group)

        # Dedicated notification for user1
        self.user_notification = Notification.objects.create(
            title="User Notification",
            content="This is a notification for user1",
            notification_type="dedicated",
            delivery_method="inApp",
            user=self.user1,
        )

        # Notification for user2 (should not be visible to user1)
        self.other_user_notification = Notification.objects.create(
            title="Other User Notification",
            content="This is a notification for user2",
            notification_type="dedicated",
            delivery_method="inApp",
            user=self.user2,
        )

    def test_list_notifications(self):
        """Test listing notifications for authenticated user"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should see both group notification and user notification
        self.assertEqual(len(response.data), 2)

        # Verify notifications are in response
        notification_ids = [n["id"] for n in response.data]
        self.assertIn(str(self.group_notification.id), notification_ids)
        self.assertIn(str(self.user_notification.id), notification_ids)
        self.assertNotIn(str(self.other_user_notification.id), notification_ids)

    def test_list_notifications_unauthenticated(self):
        """Test listing notifications without authentication"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notifications_different_user(self):
        """Test listing notifications for a different user"""
        # Authenticate as user2
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only see their own notification
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.other_user_notification.id))

    def test_notification_fields(self):
        """Test notification response fields"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification = response.data[0]
        self.assertIn("id", notification)
        self.assertIn("title", notification)
        self.assertIn("content", notification)
        self.assertIn("notification_type", notification)
        self.assertIn("delivery_method", notification)
        self.assertIn("created_at", notification)
        self.assertIn("updated_at", notification)
