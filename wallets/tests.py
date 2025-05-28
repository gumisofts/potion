from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from wallets.models import AccessKey, Transaction, Wallet

User = get_user_model()


class WalletViewsetTest(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            first_name="testuser1", phone_number="912345678", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            first_name="testuser2", phone_number="987654321", password="testpass123"
        )

        # Create wallets
        self.wallet1 = Wallet.objects.create(user=self.user1, balance=1000)
        self.wallet2 = Wallet.objects.create(user=self.user2, balance=500)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.url = reverse("wallet-list")

    def test_list_wallets(self):
        """Test listing wallets"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see own wallet
        self.assertEqual(response.data[0]["id"], str(self.wallet1.id))

    def test_list_wallets_with_filters(self):
        """Test listing wallets with filters"""
        # Test with user_id filter
        response = self.client.get(f"{self.url}?user_id={self.user1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.wallet1.id))

        # Test with phone_number filter
        response = self.client.get(f"{self.url}?phone_number={self.user1.phone_number}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.wallet1.id))

    def test_retrieve_wallet(self):
        """Test retrieving a specific wallet"""
        url = reverse("wallet-detail", args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.wallet1.id))
        self.assertEqual(response.data["balance"], self.wallet1.balance)

    def test_retrieve_other_user_wallet(self):
        """Test retrieving another user's wallet"""
        url = reverse("wallet-detail", args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        """Test accessing endpoints without authentication"""
        self.client.logout()

        # Test list endpoint
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test retrieve endpoint
        url = reverse("wallet-detail", args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class WalletPublicViewsetTest(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            first_name="testuser1", phone_number="912345678", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            first_name="testuser2", phone_number="987654321", password="testpass123"
        )

        # Create wallets
        self.wallet1 = Wallet.objects.create(user=self.user1, balance=1000)
        self.wallet2 = Wallet.objects.create(user=self.user2, balance=500)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.url = reverse("wallets-public-list")

    def test_list_public_wallets(self):
        """Test listing public wallet information"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see all wallets

        # Verify sensitive fields are excluded
        wallet_data = response.data[0]
        self.assertNotIn("balance", wallet_data)
        self.assertNotIn("frozen_amount", wallet_data)

    def test_list_public_wallets_with_filters(self):
        """Test listing public wallets with filters"""
        # Test with user_id filter
        response = self.client.get(f"{self.url}?user_id={self.user1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.wallet1.id))

        # Test with phone_number filter
        response = self.client.get(f"{self.url}?phone_number={self.user1.phone_number}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.wallet1.id))


class TransactionViewsetTest(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            first_name="testuser1", phone_number="912345678", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            first_name="testuser2", phone_number="987654321", password="testpass123"
        )

        # Create wallets
        self.wallet1 = Wallet.objects.create(user=self.user1, balance=1000)
        self.wallet2 = Wallet.objects.create(user=self.user2, balance=500)

        # Create transactions
        self.transaction1 = Transaction.objects.create(
            from_wallet=self.wallet1,
            to_wallet=self.wallet2,
            amount=100,
            remarks="Test transaction 1",
            status="completed",
        )
        self.transaction2 = Transaction.objects.create(
            from_wallet=self.wallet2,
            to_wallet=self.wallet1,
            amount=50,
            remarks="Test transaction 2",
            status="completed",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.url = reverse("transactions-list")

    def test_list_transactions(self):
        """Test listing transactions"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see all transactions

    def test_list_transactions_with_wallet_filter(self):
        """Test listing transactions with wallet filter"""
        response = self.client.get(f"{self.url}?wallet={self.wallet1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 2
        )  # Should see transactions involving wallet1

    def test_retrieve_transaction(self):
        """Test retrieving a specific transaction"""
        url = reverse("transactions-detail", args=[self.transaction1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.transaction1.id))
        self.assertEqual(response.data["amount"], self.transaction1.amount)
        self.assertEqual(response.data["status"], self.transaction1.status)
        self.assertIn("to_user", response.data)
        self.assertIn("to_business", response.data)
        self.assertIn("to_enterprise", response.data)


class SendMoneyP2PViewsetTest(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            first_name="testuser1", phone_number="912345678", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            first_name="testuser2", phone_number="987654321", password="testpass123"
        )

        # Create wallets
        self.wallet1 = Wallet.objects.create(user=self.user1, balance=1000)
        self.wallet2 = Wallet.objects.create(user=self.user2, balance=500)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.url = reverse("send-p2p-list")

    def test_send_money_success(self):
        """Test successful money transfer"""
        payload = {
            "from_wallet": self.wallet1.id,
            "to_wallet": self.wallet2.id,
            "amount": 100,
            "remarks": "Test transfer",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify transaction was created
        transaction = Transaction.objects.get(
            from_wallet=self.wallet1, to_wallet=self.wallet2
        )
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.remarks, "Test transfer")

        # Verify wallet balances were updated
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet1.balance, 900)  # 1000 - 100
        self.assertEqual(self.wallet2.balance, 600)  # 500 + 100

    def test_send_money_insufficient_balance(self):
        """Test money transfer with insufficient balance"""
        payload = {
            "from_wallet": self.wallet1.id,
            "to_wallet": self.wallet2.id,
            "amount": 2000,  # More than wallet1's balance
            "remarks": "Test transfer",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)

    def test_send_money_invalid_amount(self):
        """Test money transfer with invalid amount"""
        payload = {
            "from_wallet": self.wallet1.id,
            "to_wallet": self.wallet2.id,
            "amount": 5,  # Less than minimum amount (10)
            "remarks": "Test transfer",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)


class ReceiveMoneyExternalViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name="Test User",
            password="testpass123",
            phone_number="912345678",
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=1000.00)
        self.client = APIClient()
        # Add required headers for external system access
        AccessKey.objects.create(
            access_id="test_access_id",
            access_secret="test_access_secret",
        )
        self.client.credentials(
            HTTP_X_ACCESS_ID="test_access_id", HTTP_X_ACCESS_SECRET="test_access_secret"
        )
        self.url = reverse("receive-money-external-list")

    def test_receive_money_success(self):
        data = {
            "phone_number": self.user.phone_number,
            "amount": 500.00,
            "description": "External payment",
            "remarks": "Payment from external source",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 1500.00)

    def test_receive_money_invalid_amount(self):
        data = {
            "user_id": self.user.id,
            "amount": -100.00,
            "description": "Invalid amount",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_receive_money_nonexistent_user(self):
        data = {
            "phone_number": 987654321,
            "amount": 100.00,
            "remarks": "Nonexistent user",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_receive_money_unauthorized(self):
        # Test without access headers
        self.client.credentials()  # Remove headers
        data = {
            "user_id": self.user.id,
            "amount": 100.00,
            "description": "Unauthorized access",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
