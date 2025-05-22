import secrets
from uuid import uuid4

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import ValidationError

from .models import *


class EnterpriseSerializer(ModelSerializer):
    class Meta:
        exclude = []
        model = Enterprise


class UserGrantSerializer(ModelSerializer):
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        exclude = ["user"]
        read_only_fields = ["grant_status", "is_active"]
        model = UserGrant

    def validate(self, attrs):
        attrs = super().validate(attrs)

        phone_number = attrs.pop("phone_number")

        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            raise ValidationError(
                {"phone_number": "user with phone number is not found"}
            )

        attrs["user"] = user

        return attrs


class UserGrantSerializerForUser(ModelSerializer):
    enterprise = EnterpriseSerializer(read_only=True)

    class Meta:
        exclude = ["user"]
        model = UserGrant


class AccessGrantSerializer(ModelSerializer):
    enterprise = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AccessGrant
        exclude = []
        read_only_fields = ("access_id", "access_secret")

    def validate(self, attrs):
        attrs["access_id"] = uuid4().hex.capitalize()
        attrs["access_secret"] = secrets.token_hex(32)
        return super().validate(attrs)

    def create(self, validated_data):
        instance = super().create(validated_data)

        instance.access_secret = validated_data.pop("access_secret")

        return instance
