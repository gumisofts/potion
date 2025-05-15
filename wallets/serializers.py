from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.validators import ValidationError

from accounts.serializers import BusinessSerializer, UserGeneralInfoSerializer
from enterprises.serializers import EnterpriseSerializer
from wallets.models import *


class WalletSerializers(ModelSerializer):
    class Meta:
        exclude = []
        model = Wallet


class WalletPublicSerializer(ModelSerializer):
    class Meta:
        depth = 1
        exclude = ["balance", "frozen_amount"]
        model = Wallet


class TransactionSerializer(ModelSerializer):
    to_user = serializers.SerializerMethodField()
    to_business = serializers.SerializerMethodField()
    to_enterprise = serializers.SerializerMethodField()

    def get_to_user(self, instance):

        if instance.to_wallet and instance.to_wallet.user:
            return UserGeneralInfoSerializer(instance.to_wallet.user).data

        return None

    def get_to_business(self, instance):
        return (
            BusinessSerializer(instance.to_wallet.business).data
            if instance.to_wallet and instance.to_wallet.business
            else None
        )

    def get_to_enterprise(self, instance):
        return (
            EnterpriseSerializer(instance.to_wallet.enterprise).data
            if instance.to_wallet and instance.to_wallet.enterprise
            else None
        )

    class Meta:
        model = Transaction
        exclude = []


class SendMoneyP2PSerializer(Serializer):
    from_wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.filter())
    to_wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.filter())
    amount = serializers.IntegerField(min_value=10)
    remarks = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)

        amount = attrs.get("amount")

        wallet = attrs.get("from_wallet")

        if wallet.balance < amount:
            raise ValidationError({"amount": ["not enough amount in the wallet"]}, 400)

        return attrs

    def create(self, validated_data):
        tr = Transaction.objects.create(**validated_data)

        return tr
