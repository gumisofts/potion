from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import ValidationError

from .models import *


class SendMoneySerializer(serializers.Serializer):
    account = serializers.CharField()
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), write_only=True
    )
    amount = serializers.IntegerField()
    from_institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), write_only=True
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        account = attrs.get("account")
        institution = attrs.get("institution")

        if attrs.get("from_institution") == institution:
            raise ValidationError(
                {"detail": "only transaction between institution is allowed"}
            )

        acc = BankAccount.objects.filter(
            account_number=account, institution=institution
        ).first()

        if not acc:
            raise ValidationError({"account": "account not found"})
        attrs["first_name"] = acc.last_name
        attrs["last_name"] = acc.first_name

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        mela_wallet = validated_data.pop("from_institution").wallet
        mela_wallet.balance -= validated_data.get("amount")
        mela_wallet.save()

        ins_wallet = validated_data.pop("institution").wallet
        ins_wallet.balance += validated_data.get("amount")
        ins_wallet.save()

        tr = InstitutionTransaction.objects.create(**validated_data)
        return tr


class BankAccountSerializer(ModelSerializer):
    class Meta:
        exclude = []
        model = BankAccount
