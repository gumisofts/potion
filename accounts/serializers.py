from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import password_validation
from .models import *
from .dispatch import *
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from uuid import UUID

phone_validator = RegexValidator(
    regex=r"^(7|9)\d{8}$",
    message="Phone number must be 8-12 digits (e.g., +251945678903).",
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)

        # Add custom claims to the token payload
        token["username"] = user.username
        token["email"] = user.email
        token["phone_number"] = user.phone_number
        token["is_staff"] = user.is_staff
        token["custom_data"] = "This is custom data"

        return token


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
        )
        user.set_password(password)
        user.save()

        user_registered.send(User, **{"instance": user, "method": "PHONE"})

        return user


class CreateVerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    user_id = serializers.UUIDField(write_only=True)
    code_type = serializers.ChoiceField([(1, "PHONE"), (2, "EMAIL")], write_only=True)

    detail = serializers.SerializerMethodField()

    def get_detail(self, instance):
        return "Success"

    def create(self, validated_data):
        code = validated_data.get("code")
        code_type = validated_data.get("code_type")
        user_id = validated_data.get("user_id")

        queryset = VerificationCode.objects.filter(
            user__id=user_id, code_type=code_type, is_used=False
        )

        print(queryset)
        instance = get_object_or_404(queryset, token=hash256(code))

        if code_type == 1:
            instance.user.is_phone_verified = True
        else:
            instance.user.is_email_verified = True
        instance.is_used = True
        instance.user.save()
        instance.save()

        return instance
