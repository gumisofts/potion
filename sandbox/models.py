from django.db import models

from core.models import BaseModel


class Institution(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True, null=True)
    is_active = models.BooleanField(default=False)


class InstitutionWallet(BaseModel):
    institution = models.OneToOneField(
        Institution, on_delete=models.PROTECT, related_name="wallet"
    )
    balance = models.PositiveBigIntegerField()


class InstitutionTransaction(BaseModel):
    amount = models.PositiveBigIntegerField()
    account = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class BankAccount(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
