from unittest import mock
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from accounts.models import (
    TemporaryCode, 
    VerificationCode,
    Business,
    Service,
    User
)
from accounts.serializers import (
    CreateVerificationCodeSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    UserLoginSerializer,
)
from accounts.signals import create_business_wallet
from core.utils import hash256

from django.db.models.signals import post_save

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    SECRET_KEY="test-key",
)
class UserModelTest(TestCase):
    def setUp(self):
        self.valid_phone = "912345678"
        self.invalid_phone = "812345678"  # Doesn't start with 7 or 9
        self.password = "TestPass123!"

    def test_create_user(self):
        user = User.objects.create(
            phone_number=self.valid_phone,
            first_name="Test",
            password=self.password,
        )
        self.assertEqual(user.phone_number, self.valid_phone)
        self.assertEqual(user.first_name, "Test")
        self.assertFalse(user.is_phone_verified)
        self.assertFalse(user.is_email_verified)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            phone_number=self.valid_phone,
            first_name="Admin",
            password=self.password,  # Added required password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_phone_verified)
        self.assertTrue(user.is_email_verified)

    def test_phone_validation(self):
        with self.assertRaises(ValidationError):
            # Need to use User.objects.create() since create_user doesn't exist
            user = User(
                phone_number=self.invalid_phone,
                first_name="Test",
            )
            user.full_clean()  # This will trigger validation

    def test_user_str_representation(self):
        user = User.objects.create(
            phone_number=self.valid_phone,
            first_name="Test",
            password=self.password,
        )
        self.assertEqual(str(user), self.valid_phone)


class VerificationCodeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            phone_number="912345678",
            first_name="Test",
            password="TestPass123!",
        )
        self.expires_at = timezone.now() + timedelta(minutes=5)  # timezone-aware

    def test_verification_code_creation(self):
        code = VerificationCode.objects.create(
            token="123456",
            expires_at=self.expires_at,
            user=self.user,
            code_type=1,  # PHONE
        )
        self.assertEqual(code.user, self.user)
        self.assertEqual(code.code_type, 1)
        self.assertFalse(code.is_used)

    @patch('accounts.models.hash256')
    def test_token_hashing_on_save(self, mock_hash256):
        mock_hash256.return_value = "hashed_token"
        code = VerificationCode(
            token="123456",
            expires_at=self.expires_at,
            user=self.user,
            code_type=1,
        )
        code.save()
        mock_hash256.assert_called_once_with("123456")
        self.assertEqual(code.token, "hashed_token")


class RegisterSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "phone_number": "912345678",
            "first_name": "Test",
            "password": "StrongPass123!",
        }

    def test_valid_registration(self):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_password_validation(self):
        weak_data = self.valid_data.copy()
        weak_data["password"] = "123"
        serializer = RegisterSerializer(data=weak_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    @patch('accounts.dispatch.user_registered.send')
    def test_create_user(self, mock_signal):
        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        self.assertEqual(user.phone_number, self.valid_data["phone_number"])
        mock_signal.assert_called_once()

    def test_phone_number_validation(self):
        invalid_data = self.valid_data.copy()
        invalid_data["phone_number"] = "812345678"  # Invalid prefix
        serializer = RegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)


class UserLoginSerializerTest(TestCase):
    
    def setUp(self):
        self.password = "TestPass123!"
        self.user = User.objects.create(
            phone_number="912345678",
            first_name="Test",
        )
        self.user.set_password(self.password)  # Hash password
        self.user.save()
        self.valid_data = {
            "phone_number": "912345678",
            "password": self.password,
        }

    def test_valid_login(self):
        serializer = UserLoginSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_invalid_credentials(self):
        invalid_data = self.valid_data.copy()
        invalid_data["password"] = "wrongpassword"
        serializer = UserLoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)
        self.assertIn("password", serializer.errors)

    def test_token_generation(self):
        serializer = UserLoginSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        
        self.assertIn("refresh", tokens)
        self.assertIn("access", tokens)
        self.assertIn("user", tokens)
        self.assertEqual(tokens["user"], self.user)


class VerificationCodeSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            phone_number="912345678",
            first_name="Test",
            password="TestPass123!",
        )
        self.code = "123456"
        # Store hashed code
        self.verification_code = VerificationCode.objects.create(
            token=hash256(self.code),
            expires_at=timezone.now() + timedelta(minutes=5),
            user=self.user,
            code_type=1,
        )
        self.valid_data = {
            "code": self.code,
            "user_id": str(self.user.id),
            "code_type": 1,
        }

    def test_valid_verification(self):
        serializer = CreateVerificationCodeSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_code(self):
        invalid_data = self.valid_data.copy()
        invalid_data["code"] = "000000"  # This won't match our hashed code
        serializer = CreateVerificationCodeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    @patch('accounts.dispatch.user_phone_verified.send')
    def test_verification_process(self, mock_signal):
        serializer = CreateVerificationCodeSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        self.assertTrue(instance.is_used)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_phone_verified)
        mock_signal.assert_called_once()


class ResendVerificationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            phone_number="912345678",
            first_name="Test",
            password="TestPass123!",
        )
        self.valid_data = {
            "user_id": self.user.id,
            "code_type": 1,  # PHONE
        }

    @patch('accounts.dispatch.send_verification_code.send')
    @patch('core.utils.generate_secure_six_digits')
    def test_resend_verification(self, mock_generate, mock_signal):
        mock_generate.return_value = "654321"
        serializer = ResendVerificationSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        mock_signal.assert_called_once_with(
            sender=User,
            instance=self.user,
            code_type=1,
            code="654321"
        )


class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.register_url = "/accounts/register/"
        self.login_url = "/accounts/login/"
        self.verify_url = "/accounts/verifications/confirm/"
        self.resend_url = "/accounts/verifications/resend/"

        self.valid_user_data = {
            "phone_number": "912345678",
            "first_name": "Test",
            "password": "TestPass123!",
        }
        self.user = User.objects.create(
            phone_number=self.valid_user_data["phone_number"],
            first_name=self.valid_user_data["first_name"],
            password=self.valid_user_data["password"],  # Password will be hashed
        )
        self.user.is_active = True
        self.user.save()

    @patch('accounts.dispatch.user_registered.send')
    def test_user_registration(self, mock_signal):
        new_user_data = {
            "phone_number": "987654321",
            "first_name": "New",
            "password": "NewPass123!",
        }
        
        response = self.client.post(self.register_url, new_user_data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(phone_number="987654321").exists())
        mock_signal.assert_called_once()

    def test_user_login(self):
        response = self.client.post(self.login_url, {
            "phone_number": self.valid_user_data["phone_number"],
            "password": self.valid_user_data["password"],
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)

    @patch('accounts.dispatch.send_verification_code.send')
    @patch('core.utils.generate_secure_six_digits')
    def test_verification_code_resend(self, mock_generate, mock_signal):
        mock_generate.return_value = "123456"
        mock_signal.return_value = [MagicMock()]
        
        response = self.client.post(self.resend_url, {
            "user_id": self.user.id,
            "code_type": 1,
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(VerificationCode.objects.filter(user=self.user).exists())
        mock_signal.assert_called_once()

    @patch('accounts.dispatch.user_phone_verified.send')
    def test_verification_code_confirmation(self, mock_signal):
        code = "123456"
        VerificationCode.objects.create(
            token=hash256(code),
            expires_at=timezone.now() + timedelta(minutes=5),
            user=self.user,
            code_type=1,
        )
        
        response = self.client.post(self.verify_url, {
            "code": code,
            "user_id": str(self.user.id),
            "code_type": 1,
        })
        
        self.assertEqual(response.status_code, 201)
        mock_signal.assert_called_once_with(sender=User, instance=self.user)


class BusinessModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            phone_number="912345678",
            first_name="Test",
            password="TestPass123!",
        )
        self.business_data = {
            "owner": self.user,
            "name": "Test Business",
            "contact_email": "test@example.com",
            "license_id": uuid.uuid4(),
        }

        post_save.disconnect(receiver=create_business_wallet, sender=Business)

    @patch('accounts.signals.create_business_wallet')
    def test_business_creation(self, mock_signal):
        business = Business.objects.create(**self.business_data)
        mock_signal.assert_called_once_with(
            sender=Business,
            instance=business,
            created=True,
            raw=False,
            using="default",
            update_fields=None
        )

class ServiceModelTest(TestCase):
    @patch('accounts.signals.create_business_wallet')
    def setUp(self, mock_signal):
        self.user = User.objects.create(
            phone_number="912345678",
            first_name="Test",
            password="TestPass123!",
        )
        self.business = Business.objects.create(
            owner=self.user,
            name="Test Business",
            contact_email="test@example.com",
            license_id=uuid.uuid4(),
        )
    def test_service_creation(self):
        service = Service.objects.create(
            business=self.business,
            name="Test Service",
            service_type="basic",
        )
        self.assertEqual(service.name, "Test Service")
        self.assertEqual(service.service_type, "basic")
        self.assertTrue(service.is_active)

    def test_service_str_representation(self):
        service = Service.objects.create(
            business=self.business,
            name="Test Service",
            service_type="premium",
        )
        self.assertEqual(str(service), "Test Service (premium)")