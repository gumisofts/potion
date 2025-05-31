from datetime import datetime, timedelta
from uuid import UUID

from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils import generate_secure_six_digits

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
            "id",
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
        fields = (
            "id",
            "first_name",
            "last_name",
            "password",
            "phone_number",
            "date_joined",
        )
        read_only_fields = ["id"]

    def validate(self, attrs):
        user = User(**attrs)
        try:
            password_validation.validate_password(attrs.get("password"), user)
        except ValidationError as e:
            raise ValidationError({"password": e})

        return super().validate(attrs)

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

        phone_number = User.normalize_phone_number(phone_number)

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


class BusinessSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    trust_level = serializers.HiddenField(default="medium")
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Business
        exclude = []


class BusinessServiceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Service
        exclude = []


class UserDeviceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserDevice
        exclude = ["is_last_time_used_device"]


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = []


class RequestPasswordResetSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)

    def validate_phone_number(self, value):
        phone_number = User.normalize_phone_number(value)
        if not User.objects.filter(phone_number=phone_number, is_active=True).exists():
            raise serializers.ValidationError("No user found with this phone number")
        return phone_number

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number")
        user = User.objects.get(phone_number=phone_number)

        # Generate a new verification code
        token = generate_secure_six_digits()
        VerificationCode.objects.create(
            expires_at=timezone.now() + timedelta(minutes=5),
            token=token,
            code_type=1,  # Using PHONE type
            user=user,
        )
        TemporaryCode.objects.create(code=token, phone_number=phone_number)

        return {"detail": "Password reset code has been sent to your phone number"}


class ConfirmPasswordResetSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    phone_number = serializers.SlugRelatedField(
        slug_field="phone_number",
        write_only=True,
        queryset=User.objects.filter(is_active=True, is_phone_verified=True),
    )
    new_password = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        code = attrs.get("code")
        user = attrs.get("phone_number")
        new_password = attrs.get("new_password")

        # First validate the new password
        try:
            password_validation.validate_password(new_password, user)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User not found"})
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e})

        # Then validate the verification code
        queryset = VerificationCode.objects.filter(
            user=user,
            code_type=1,  # PHONE type
            is_used=False,
            expires_at__gt=timezone.now(),  # Check if code is not expired
        )
        try:
            instance = queryset.get(token=hash256(code))
            attrs["verification_code"] = instance
            attrs["user"] = user
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid or expired code"})

        return attrs

    def create(self, validated_data):
        verification_code = validated_data.pop("verification_code")
        new_password = validated_data.pop("new_password")
        user = validated_data.pop("user")

        # Update user's password
        user.set_password(new_password)
        user.save()

        # Mark verification code as used
        verification_code.is_used = True
        verification_code.save()

        return {"detail": "Password has been reset successfully"}


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["groups", "user_permissions", "is_superuser", "is_staff", "password"]


class BusinessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "date_joined",
        ]


# Business Wallets
# Stats
# External Bank accounts
# Popular Subs(amount, count)
# Receipt Generations
# Monthly Revenue
