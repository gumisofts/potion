from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.validators import ValidationError

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

        attrs["amount"] = -1 * amount

        return attrs

    def create(self, validated_data):
        tr = Transaction.objects.create(**validated_data)

        return tr
