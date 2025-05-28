from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bills.models import Billing, Utility, UtilityUser
from wallets.models import Wallet

User = get_user_model()


class UtilityViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("utilities-list")

        # Create test utilities
        self.utility1 = Utility.objects.create(name="Electricity")
        self.utility2 = Utility.objects.create(name="Water")

    def test_list_utilities(self):
        """Test listing all utilities"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], self.utility1.name)
        self.assertEqual(response.data[1]["name"], self.utility2.name)


class PaybillsViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("pay-bills-list")

        # Create wallet for user
        self.wallet = Wallet.objects.create(user=self.user, balance=1000)

        # Create utility and utility user
        self.utility = Utility.objects.create(name="Electricity")
        self.utility_user = UtilityUser.objects.create(
            number=123456789, phone_number="912345678"
        )

        # Create unpaid bills
        self.bill1 = Billing.objects.create(
            utility=self.utility,
            user=self.utility_user,
            amount=100,
            due_date=timezone.now(),
            is_paid=False,
        )
        self.bill2 = Billing.objects.create(
            utility=self.utility,
            user=self.utility_user,
            amount=200,
            due_date=timezone.now(),
            is_paid=False,
        )

    def test_pay_bills_success(self):
        """Test successful bill payment"""
        payload = {
            "number": self.utility_user.number,
            "amount": 300,  # Total of both bills
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "success")

        # Verify bills are marked as paid
        self.bill1.refresh_from_db()
        self.bill2.refresh_from_db()
        self.assertTrue(self.bill1.is_paid)
        self.assertTrue(self.bill2.is_paid)

        # Verify wallet balance is updated
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 700)  # 1000 - 300

    def test_pay_bills_insufficient_amount(self):
        """Test bill payment with insufficient amount"""
        payload = {
            "number": self.utility_user.number,
            "amount": 200,  # Less than total bills (300)
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)

    def test_pay_bills_insufficient_balance(self):
        """Test bill payment with insufficient wallet balance"""
        self.wallet.balance = 100
        self.wallet.save()

        payload = {"number": self.utility_user.number, "amount": 300}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)

    def test_pay_bills_no_due_bills(self):
        """Test bill payment when there are no due bills"""
        # Mark bills as paid
        self.bill1.is_paid = True
        self.bill1.save()
        self.bill2.is_paid = True
        self.bill2.save()

        payload = {"number": self.utility_user.number, "amount": 300}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("number", response.data)


class BillsViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create utility and utility user
        self.utility = Utility.objects.create(name="Electricity")
        self.utility_user = UtilityUser.objects.create(
            number=123456789, phone_number="912345678"
        )

        # Create unpaid bills
        self.bill1 = Billing.objects.create(
            utility=self.utility,
            user=self.utility_user,
            amount=100,
            due_date=timezone.now(),
            is_paid=False,
        )
        self.bill2 = Billing.objects.create(
            utility=self.utility,
            user=self.utility_user,
            amount=200,
            due_date=timezone.now(),
            is_paid=False,
        )

    def test_retrieve_unpaid_bills(self):
        """Test retrieving unpaid bills for a user"""
        url = reverse("unpaid-bills-detail", args=[self.utility_user.number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["amount"], 300)  # Total of both bills

    def test_retrieve_unpaid_bills_nonexistent_user(self):
        """Test retrieving unpaid bills for a nonexistent user"""
        url = reverse("unpaid-bills-detail", args=[999999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["amount"], 0)  # No bills found

    def test_retrieve_unpaid_bills_all_paid(self):
        """Test retrieving unpaid bills when all bills are paid"""
        # Mark bills as paid
        self.bill1.is_paid = True
        self.bill1.save()
        self.bill2.is_paid = True
        self.bill2.save()

        url = reverse("unpaid-bills-detail", args=[self.utility_user.number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["amount"], 0)  # No unpaid bills
