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

        phone_number = attrs.get("phone_number")

        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            raise ValidationError(
                {"phone_number": "user with phone number is not found"}
            )

        attrs["user"] = user

        return attrs
