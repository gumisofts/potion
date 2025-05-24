from datetime import datetime, timedelta
from uuid import UUID

from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import *
from core.utils import generate_secure_six_digits
from wallets.models import *

from .models import *

phone_validator = RegexValidator(
    regex=r"^(7|9)\d{8}$",
    message="Phone number must be 8-12 digits (e.g., +251945678903).",
)


class AdminGeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "is_phone_verified",
            "is_email_verified",
            "date_joined",
        ]


class AdminLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    user = AdminGeneralInfoSerializer(read_only=True)

    def validate(self, attrs):
        password = attrs.pop("password")
        phone_number = attrs.pop("phone_number")

        phone_number = User.normalize_phone_number(phone_number)

        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise ValidationError(
                {
                    "phone_number": "No user found with the given credentials",
                    "password": "No user found with the given credentials",
                }
            )

        # Only allow logins for admin/superuser
        if not (user.is_staff or user.is_superuser):
            raise ValidationError(
                "Only admin/superuser accounts are allowed to log in."
            )

        attrs = super().validate(attrs)
        attrs["user"] = user

        return attrs

    def create(self, validated_data):
        user = validated_data.pop("user")
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user,
        }


class UsersDataSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    is_phone_verified = serializers.BooleanField(write_only=True)


class TransactionRecordSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source="created_at", format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Transaction
        fields = ["id", "from_user", "to_user", "amount", "status", "remarks", "date"]

    def get_from_user(self, obj):
        if not obj.from_wallet:
            return "external"
        if obj.from_wallet.user:
            return str(obj.from_wallet.user.id)
        elif obj.from_wallet.business:
            return f"business:{obj.from_wallet.business.id}"
        return "external"

    def get_to_user(self, obj):
        if not obj.to_wallet:
            return "external"
        if obj.to_wallet.user:
            return str(obj.to_wallet.user.id)
        return f"business:{obj.to_wallet.business.id}"


class DisputeTransactionSerializer(serializers.ModelSerializer):
    transaction = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Transaction.objects.all(),
        help_text="ID of the disputed transaction",
    )
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Dispute
        fields = [
            "id",
            "transaction",
            "phone_number",
            "amount",
            "notes",
            "status",
            "created_at",
        ]
        extra_kwargs = {
            "transaction": {"required": True},
            "amount": {"required": False},  # Make amount optional
            "created_at": {"read_only": True},
        }

    def validate_transaction(self, value):
        if not Transaction.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Transaction does not exist")
        return value


class DisputeStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ["id", "status"]
        read_only_fields = ["id"]

    def validate_status(self, value):
        instance = self.instance
        if instance and instance.status != "needs_response" and value == "in_review":
            raise serializers.ValidationError(
                "Can only move to 'in_review' from 'needs_response' status"
            )
        return value


class DisputeReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ["id", "status", "notes"]
        read_only_fields = ["id"]

    def validate(self, data):
        instance = self.instance
        if instance.status != "in_review":
            raise serializers.ValidationError(
                "Can only move to 'reviewed' from 'in_review' status"
            )
        return data


class DisputeRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ["id", "status", "notes"]
        read_only_fields = ["id"]

    def validate(self, data):
        instance = self.instance
        if instance.status != "reviewed":
            raise serializers.ValidationError("Can only refund from 'reviewed' status")
        return data


class BusinessRecordSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "contact_phone",
            "contact_email",
            "is_active",
            "is_verified",
            "owner",
            "trust_level",
            "created_at",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
        }
