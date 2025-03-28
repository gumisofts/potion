from rest_framework.serializers import ModelSerializer, Serializer, ValidationError

from wallets.models import *


class WalletSerializers(ModelSerializer):
    class Meta:
        exclude = []
        model = Wallet


class TransactionWalletSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id",
            "type",
            "amount",
            "notes",
            "status",
        )
        read_only_fields = ("id", "wallet")

    def create(self, validated_data):
        """
        Handles Create a new transaction
        """

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise ValidationError("User is not authenticated.")

        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            raise ValidationError("No wallet found for the authenticated user.")

        transaction = Transaction.objects.create(
            wallet=wallet,
            type=validated_data.get("type"),
            amount=validated_data.get("amount"),
            notes=validated_data.get("notes"),
            status=validated_data.get("status", "pending"),
        )

        return transaction

    def update(self, instance, validated_data):
        """
        Update a Transaction instance and handle wallet balance changes.
        """
        instance.status = validated_data.get("status", instance.status)

        instance.save()
        return instance
