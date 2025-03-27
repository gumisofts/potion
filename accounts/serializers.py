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

from core.utils import generate_secure_six_digits
from subscriptions.models import Subscription
from wallets.models import Wallet

from .dispatch import *
from .dispatch import user_phone_verified
from .models import *

phone_validator = RegexValidator(
    regex=r"^(7|9)\d{8}$",
    message="Phone number must be 8-12 digits (e.g., +251945678903).",
)


class UserGeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "is_phone_verified",
            "is_email_verified",
            "date_joined",
        ]


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "password", "phone_number", "date_joined")

    def validate(self, attrs):
        user = User(**attrs)
        try:
            password_validation.validate_password(attrs.get("password"), user)
        except ValidationError as e:
            raise ValidationError({"password": e})

        return attrs

    def create(self, validated_data):
        password = validated_data.get("password")

        user: User = User.objects.create(
            phone_number=validated_data.get("phone_number"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            password=validated_data.get("password"),
        )

        user_registered.send(User, **{"instance": user, "method": "PHONE"})

        return user


class CreateVerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    user_id = serializers.UUIDField(write_only=True)
    code_type = serializers.ChoiceField([(1, "PHONE"), (2, "EMAIL")], write_only=True)

    detail = serializers.SerializerMethodField()
    user = UserGeneralInfoSerializer(read_only=True)

    def get_detail(self, instance):
        return "Success"

    def create(self, validated_data):
        code = validated_data.get("code")
        code_type = validated_data.get("code_type")
        user_id = validated_data.get("user_id")

        queryset = VerificationCode.objects.filter(
            user__id=user_id, code_type=code_type, is_used=False
        )

        instance = get_object_or_404(queryset, token=hash256(code))

        if code_type == 1:
            instance.user.is_phone_verified = True
        else:
            instance.user.is_email_verified = True
        instance.is_used = True
        instance.user.save()
        instance.save()

        user_phone_verified.send(User, **{"instance": instance.user})

        return instance


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    user = UserGeneralInfoSerializer(read_only=True)

    def validate(self, attrs):
        password = attrs.pop("password")
        phone_number = attrs.pop("phone_number")

        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise ValidationError(
                {
                    "phone_number": "No user found with the given credentials",
                    "password": "no user found with the given credentials",
                }
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


class ResendVerificationSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )
    code_type = serializers.ChoiceField(choices=[(1, "PHONE"), (2, "EMAIL")])
    detail = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        code_type = validated_data.pop("code_type")
        token = generate_secure_six_digits()
        VerificationCode.objects.create(
            expires_at=datetime.now() + timedelta(minutes=5),
            token=token,
            code_type=code_type,
            user=user_id,
        )
        TemporaryCode.objects.create(code=token, phone_number=user_id.phone_number)

        return {"user_id": user_id, "code_type": code_type, "detail": "success"}


class RegisterBusinessSerializer(serializers.ModelSerializer):
    contact_email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=Business.objects.all())],
    )
    contact_phone = serializers.CharField(
        required=True,
        max_length=255,
        validators=[
            phone_validator,
            validators.UniqueValidator(queryset=Business.objects.all()),
        ],
    )

    class Meta:
        model = Business
        fields = (
            "name",
            "contact_phone",
            "contact_email",
            "license_id",
            "trust_level",
        )
        read_only_fields = ("id", "owner", "wallet")

    def create(self, validated_data):
        """
        Handles business creation.
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User is not authenticated.")

        wallet = Wallet.objects.create(user=request.user)

        business: Business = Business.objects.create(
            owner=request.user,
            name=validated_data.get("name"),
            contact_phone=validated_data.get("contact_phone"),
            contact_email=validated_data.get("contact_email"),
            license_id=validated_data.get("license_id"),
            trust_level=validated_data.get("trust_level"),
        )

        # business.save()
        return business


class BusinessDetailSerializer(serializers.ModelSerializer):
    contact_email = serializers.EmailField(
        required=False,
    )
    contact_phone = serializers.CharField(
        required=False,
        max_length=255,
        validators=[
            phone_validator,
        ],
    )

    class Meta:
        model = Business
        fields = (
            "name",
            "contact_phone",
            "contact_email",
            "license_id",
            "trust_level",
        )
        read_only_fields = ("id", "owner", "wallet")

    def update(self, instance, validated_data):
        """
        Handles business updates.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.contact_phone = validated_data.get(
            "contact_phone", instance.contact_phone
        )
        instance.contact_email = validated_data.get(
            "contact_email", instance.contact_email
        )
        instance.license_id = validated_data.get("license_id", instance.license_id)
        instance.trust_level = validated_data.get("trust_level", instance.trust_level)

        instance.save()
        return instance


class BusinessServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "service_type",
            "is_active",
        )
        read_only_fields = ("id", "business")

    def create(self, validated_data):
        """
        Handles Business service creation.
        """

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User is not authenticated.")

        # business = validated_data.get("business")
        business = Business.objects.filter(owner=request.user).first()
        if not business:
            raise serializers.ValidationError(
                "No business found for the authenticated user."
            )

        service = Service.objects.create(
            business=business,
            name=validated_data.get("name"),
            service_type=validated_data.get("service_type"),
            is_active=validated_data.get("is_active", True),
        )

        return service

    def update(self, instance, validated_data):
        """
        Handles Business service updates.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.service_type = validated_data.get(
            "service_type", instance.service_type
        )
        instance.is_active = validated_data.get("is_active", instance.is_active)

        instance.save()
        return instance


class ServiceSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            "id",
            "name",
            "frequency",
            "fixed_price",
            "has_fixed_price",
        )
        read_only_fields = ("id", "service")

    def create(self, validated_data):
        """
        Handles Business service creation.
        """

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User is not authenticated.")

        business = Business.objects.filter(owner=request.user).first()
        if not business:
            raise serializers.ValidationError(
                "No business found for the authenticated user."
            )

        service = Service.objects.filter(business=business).first()

        if not service:
            raise serializers.ValidationError(
                "No service found for the authenticated user."
            )

        subscription = Subscription.objects.create(
            service=service,
            name=validated_data.get("name"),
            frequency=validated_data.get("frequency"),
            fixed_price=validated_data.get("fixed_price"),
            has_fixed_price=validated_data.get("has_fixed_price", True),
        )

        return subscription

    def update(self, instance, validated_data):
        """
        Handles Service subscription updates.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.frequency = validated_data.get("frequency", instance.frequency)
        instance.fixed_price = validated_data.get("fixed_price", instance.fixed_price)
        instance.has_fixed_price = validated_data.get(
            "has_fixed_price", instance.has_fixed_price
        )

        instance.save()
        return instance
