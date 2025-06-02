from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.validators import ValidationError

from accounts.serializers import BusinessSerializer, UserGeneralInfoSerializer
from enterprises.serializers import EnterpriseSerializer
from wallets.external_handler import *
from wallets.models import *
from rest_framework.response import Response


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

        if wallet == attrs.get("to_wallet"):
            raise ValidationError(
                {"to_wallet": ["You cannot send money to the same wallet"]}, 400
            )

        return attrs

    def create(self, validated_data):
        tr = Transaction.objects.create(**validated_data)

        return tr


class ReceiveMoneyExternalSerializer(Serializer):
    phone_number = serializers.SlugRelatedField(
        queryset=User.objects.filter(is_active=True),
        slug_field="phone_number",
        write_only=True,
    )
    amount = serializers.IntegerField(min_value=10)
    remarks = serializers.CharField()
    details = serializers.CharField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        amount = attrs.get("amount")

        user = attrs.pop("phone_number")

        wallet = user.wallet

        attrs["to_wallet"] = wallet

        return attrs

    def create(self, validated_data):
        tr = Transaction.objects.create(**validated_data)
        tr.details = "success"

        return tr


class SendMoneyExternalSerializer(Serializer):
    from_wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.filter())
    bank = serializers.CharField(write_only=True)
    account_number = serializers.CharField(write_only=True)
    amount = serializers.IntegerField(min_value=10)
    remarks = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)

        amount = attrs.get("amount")

        wallet = attrs.get("from_wallet")

        if wallet.balance < amount:
            raise ValidationError({"amount": ["not enough amount in the wallet"]}, 400)

        if wallet != self.context.get("request").user.wallet:
            raise ValidationError(
                {"from_wallet": ["You can only send money from your own wallet"]}, 400
            )

        # Sending money to external bank

        acc = attrs.pop("account_number", None)
        bank = attrs.pop("bank", None)

        send_money_external(acc, bank, amount, attrs.get("remarks", ""))

        return attrs

    def create(self, validated_data):
        tr = Transaction.objects.create(**validated_data)

        return tr


# class TransactionStatsSerializer()
# Dashboard apis
class TransactionStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "amount", "created_at", "updated_at"]
