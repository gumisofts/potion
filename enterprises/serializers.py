import secrets
from uuid import uuid4

from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import ValidationError

from wallets.models import Transaction, Wallet

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
        attrs["is_active"] = True

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


class PullWalletMoneySerializer(serializers.Serializer):
    enterprise = serializers.HiddenField(default=serializers.CurrentUserDefault())
    amount = serializers.IntegerField(min_value=1)
    remarks = serializers.CharField(required=False, allow_blank=True)
    user_grant = serializers.PrimaryKeyRelatedField(
        queryset=UserGrant.objects.filter(is_active=True, enterprise__isnull=False)
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        amount = attrs.get("amount")
        enterprise = attrs.get("enterprise")
        user_grant = attrs.get("user_grant")
        if not user_grant.enterprise == enterprise:
            raise ValidationError(
                {"user_grant": "User grant does not belong to this enterprise"}
            )
        if enterprise.is_active is False:
            raise ValidationError({"enterprise": "Enterprise is not active"})
        if user_grant.grant_status != "approved":
            raise ValidationError(
                {"user_grant": "User grant is not approved or is suspended"}
            )
        if user_grant.max_amount < amount:
            raise ValidationError(
                {"amount": "Amount exceeds the maximum allowed for this user grant"}
            )
        if user_grant.expires_at and user_grant.expires_at < timezone.now():
            raise ValidationError({"user_grant": "User grant has expired"})
        if not user_grant.is_active:
            raise ValidationError({"user_grant": "User grant is not active"})

        return attrs

    def create(self, validated_data):
        tr = Transaction.objects.create(
            to_wallet=validated_data["enterprise"].wallet,
            from_wallet=validated_data["user_grant"].user.wallet,
            amount=validated_data["amount"],
            remarks=validated_data.get("remarks", ""),
        )
        return validated_data
