from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from wallets.models import *


class WalletSerializers(ModelSerializer):
    class Meta:
        exclude = []
        model = Wallet


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        exclude = []


class SendMoneyP2PSerializer(Serializer):
    amount = serializers.IntegerField(min_value=10)
    from_wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.filter())
    to_wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.filter())
    remarks = serializers.CharField()

    def create(self, validated_data):
        pass
