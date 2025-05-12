from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import ValidationError

from bills.models import *
from wallets.models import Transaction


class PayUtilitySerializer(serializers.Serializer):
    number = serializers.CharField(write_only=True)
    amount = serializers.IntegerField(write_only=True)
    detail = serializers.CharField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        bills = Billing.objects.filter(
            user__number=attrs.get("number"),
            due_date__lte=timezone.now(),
            is_paid=False,
        )

        if not bills.exists():
            raise ValidationError({"number": "no due bills"})

        user = self.context.get("request").user
        if user.wallet.balance - user.wallet.frozen_amount < attrs.get("amount"):
            raise ValidationError({"amount": "insufficient wallet balance"})

        total = bills.aggregate(total=Sum("amount")).get("total")

        if attrs.get("amount") < total:
            raise ValidationError(
                {"amount": "amount is not sufficient to settle all the billings"}
            )

        attrs["bills"] = bills

        attrs["wallet"] = user.wallet

        return attrs

    def create(self, validated_data):
        bills = validated_data.pop("bills")
        wallet = validated_data.pop("wallet")

        with transaction.atomic():

            for bill in bills:

                bill.is_paid = True
                bill.save()

                Transaction.objects.create(
                    from_wallet=wallet,
                    amount=bill.amount,
                    remarks=f"Bills Payment for {bill.utility.name} for {bill.due_date}",
                )

        return {"detail": "success"}
