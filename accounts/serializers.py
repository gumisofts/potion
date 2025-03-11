from django.contrib.auth.password_validation import validate_password
from django.core.validators import (
    RegexValidator,
)
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

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


class RegisterSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(required=False)
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(required=True, validators=[validate_password])
    phone_number = serializers.CharField(
        required=True,
        max_length=255,
        validators=[
            phone_validator,
            validators.UniqueValidator(queryset=User.objects.all()),
        ],
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "password",
            "password_confirmation",
            "email",
            "phone_number",
        )

    def validate(self, data):
        if data["password"] != data["password_confirmation"]:
            raise exceptions.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return data

    def create(self, validated_data):
        user: User = User.objects.create(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )

        user.set_password(validated_data.get("password"))
        user.save()

        return user
