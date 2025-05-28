from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import Business, Service
from subscriptions.models import Subscription, SubscriptionFeature, UserSubscription
from wallets.models import Wallet

User = get_user_model()


class SubscribeViewsetTest(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=1000)

        # Create test business and service
        self.business = Business.objects.create(
            name="Test Business",
            owner=self.user,
            contact_phone="912345678",
            contact_email="test@example.com",
            is_verified=True,
        )
        self.service = Service.objects.create(
            name="Test Service", business=self.business, service_type="basic"
        )

        # Create test subscription
        self.subscription = Subscription.objects.create(
            name="Test Subscription",
            service=self.service,
            frequency=30,  # 30 days
            fixed_price=100,
            has_fixed_price=True,
            payment_type="pre",
            is_active=True,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("subscribe-service-list")

    def test_subscribe_success(self):
        """Test successful subscription"""
        payload = {"subscription": self.subscription.id}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify subscription was created
        user_sub = UserSubscription.objects.get(
            user=self.user, subscription=self.subscription
        )
        self.assertTrue(user_sub.is_active)
        self.assertIsNotNone(user_sub.next_billing_date)

        # Verify wallet balance was updated
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 900)  # 1000 - 100

    def test_subscribe_insufficient_balance(self):
        """Test subscription with insufficient balance"""
        self.wallet.balance = 50
        self.wallet.save()

        payload = {"subscription": self.subscription.id}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_list_subscriptions(self):
        """Test listing user's subscriptions"""
        # Create a subscription for the user
        UserSubscription.objects.create(
            user=self.user,
            subscription=self.subscription,
            is_active=True,
            next_billing_date=timezone.now(),
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["subscription"], self.subscription.id)
        self.assertTrue(response.data[0]["is_active"])

    def test_list_subscriptions_with_filters(self):
        """Test listing subscriptions with filters"""
        # Create a subscription for the user
        UserSubscription.objects.create(
            user=self.user,
            subscription=self.subscription,
            is_active=True,
            next_billing_date=timezone.now(),
        )

        # Test with subscription_id filter
        response = self.client.get(f"{self.url}?subscription_id={self.subscription.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test with next_billing_date_gt filter
        future_date = timezone.now() + timezone.timedelta(days=1)
        response = self.client.get(
            f"{self.url}?next_billing_date_gt={future_date.date().isoformat()}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class UnSubscribeViewsetTest(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )
        # Create wallet for user
        self.wallet = Wallet.objects.create(user=self.user, balance=1000)

        # Create test business and service
        self.business = Business.objects.create(
            name="Test Business",
            owner=self.user,
            contact_phone="912345678",
            contact_email="test@example.com",
            is_verified=True,
        )
        self.service = Service.objects.create(
            name="Test Service", business=self.business, service_type="basic"
        )

        # Create test subscription
        self.subscription = Subscription.objects.create(
            name="Test Subscription",
            service=self.service,
            frequency=30,
            fixed_price=100,
            has_fixed_price=True,
            is_active=True,
        )

        # Create active subscription for user
        self.user_sub = UserSubscription.objects.create(
            user=self.user,
            subscription=self.subscription,
            is_active=True,
            next_billing_date=timezone.now(),
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("unsubscribe-service-list")

    def test_unsubscribe_success(self):
        """Test successful unsubscription"""
        payload = {"subscription": self.subscription.id}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify subscription was deactivated
        self.user_sub.refresh_from_db()
        self.assertFalse(self.user_sub.is_active)

    def test_list_unsubscribed(self):
        """Test listing unsubscribed services"""
        # Deactivate the subscription
        self.user_sub.is_active = False
        self.user_sub.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["subscription"], self.subscription.id)
        self.assertFalse(response.data[0]["is_active"])


class SubscriptionViewsetTest(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )

        # Create test business and service
        self.business = Business.objects.create(
            name="Test Business",
            owner=self.user,
            contact_phone="912345678",
            contact_email="test@example.com",
            is_verified=True,
        )
        self.service = Service.objects.create(
            name="Test Service", business=self.business, service_type="basic"
        )

        # Create test features
        self.feature1 = SubscriptionFeature.objects.create(content="Feature 1")
        self.feature2 = SubscriptionFeature.objects.create(content="Feature 2")

        # Create test subscription
        self.subscription = Subscription.objects.create(
            name="Test Subscription",
            service=self.service,
            frequency=30,
            fixed_price=100,
            has_fixed_price=True,
            is_active=True,
        )
        self.subscription.features.add(self.feature1, self.feature2)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("subscriptions-list")

    def test_list_subscriptions(self):
        """Test listing all subscriptions"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.subscription.name)
        self.assertEqual(len(response.data[0]["features"]), 2)

    def test_list_subscriptions_with_filters(self):
        """Test listing subscriptions with filters"""
        # Test with service_id filter
        response = self.client.get(f"{self.url}?service_id={self.service.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test with business_id filter
        response = self.client.get(f"{self.url}?business_id={self.business.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test with service_type filter
        response = self.client.get(f"{self.url}?service__service_type=basic")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_subscription(self):
        """Test creating a new subscription"""
        payload = {
            "name": "New Subscription",
            "service": self.service.id,
            "frequency": 60,
            "fixed_price": 200,
            "has_fixed_price": True,
            "is_active": True,
            "features": [{"content": "New Feature 1"}, {"content": "New Feature 2"}],
        }
        response = self.client.post(self.url, payload, format="json")
        print(response.data)  # Debugging line to see the response data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Subscription")
        self.assertEqual(len(response.data["features"]), 2)

    def test_retrieve_subscription(self):
        """Test retrieving a specific subscription"""
        url = reverse("subscriptions-detail", args=[self.subscription.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.subscription.name)
        self.assertEqual(len(response.data["features"]), 2)

    def test_update_subscription(self):
        """Test updating a subscription"""
        url = reverse("subscriptions-detail", args=[self.subscription.id])
        payload = {
            "name": "Updated Subscription",
            "service": self.service.id,
            "frequency": 45,
            "fixed_price": 150,
            "has_fixed_price": True,
            "is_active": True,
            "features": [
                {"content": "Updated Feature 1"},
                {"content": "Updated Feature 2"},
            ],
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Subscription")
        self.assertEqual(response.data["frequency"], 45)
        self.assertEqual(response.data["fixed_price"], 150)

    def test_delete_subscription(self):
        """Test deleting a subscription"""
        url = reverse("subscriptions-detail", args=[self.subscription.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify subscription was deleted
        self.assertFalse(Subscription.objects.filter(id=self.subscription.id).exists())


class UserSubscriptionViewsetTest(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )

        # Create test business and service
        self.business = Business.objects.create(
            name="Test Business",
            owner=self.user,
            contact_phone="912345678",
            contact_email="test@example.com",
            is_verified=True,
        )
        self.service = Service.objects.create(
            name="Test Service", business=self.business, service_type="basic"
        )

        # Create test subscriptions
        self.subscription1 = Subscription.objects.create(
            name="Test Subscription 1",
            service=self.service,
            frequency=30,
            fixed_price=100,
            has_fixed_price=True,
            is_active=True,
        )
        self.subscription2 = Subscription.objects.create(
            name="Test Subscription 2",
            service=self.service,
            frequency=60,
            fixed_price=200,
            has_fixed_price=True,
            is_active=True,
        )

        # Create user subscriptions
        self.user_sub1 = UserSubscription.objects.create(
            user=self.user,
            subscription=self.subscription1,
            is_active=True,
            next_billing_date=timezone.now(),
        )
        self.user_sub2 = UserSubscription.objects.create(
            user=self.user,
            subscription=self.subscription2,
            is_active=False,
            next_billing_date=timezone.now(),
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user-subscriptions-list")

    def test_list_user_subscriptions(self):
        """Test listing user's subscriptions"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both active and inactive

    def test_list_user_subscriptions_with_filters(self):
        """Test listing user's subscriptions with filters"""
        # Test with is_active=True filter
        response = self.client.get(f"{self.url}?is_active=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]["is_active"])

        # Test with is_active=False filter
        response = self.client.get(f"{self.url}?is_active=False")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertFalse(response.data[0]["is_active"])
