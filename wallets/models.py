from uuid import uuid4

from django.contrib.auth.hashers import check_password, make_password
from django.core.validators import MinValueValidator
from django.db import models, transaction

from accounts.models import Business, User
from core.models import BaseModel


class Wallet(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="wallet"
    )
    business = models.OneToOneField(
        Business, on_delete=models.PROTECT, null=True, blank=True, related_name="wallet"
    )
    enterprise = models.OneToOneField(
        "enterprises.Enterprise",
        on_delete=models.PROTECT,
        related_name="wallet",
        null=True,
        blank=True,
    )
    balance = models.BigIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="Balance cannot be negative.")],
    )

    frozen_amount = models.BigIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="Frozen amount cannot be negative.")],
    )
    is_restricted = models.BooleanField(default=False)
    wallet_type = models.CharField(
        max_length=255,
        choices=[
            ("user", "user"),
            ("business", "business"),
            ("enterprise", "enterprises"),
        ],
        default="user",
    )

    def __str__(self):
        return f"Wallet ({self.user.email if self.user else 'Business'})"

    def __str__(self):
        return f"Wallet({self.id})"


class Transaction(BaseModel):
    from_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )
    to_wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, null=True, blank=True
    )
    amount = models.BigIntegerField(
        validators=[MinValueValidator(1, message="Amount must be at least 1.")]
    )

    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )

    def __str__(self):
        return f"{self.amount} (Status: {self.status})"


class AccessKey(BaseModel):
    access_id = models.CharField(max_length=255, unique=True)
    access_secret = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.access_id:
            self.access_key = str(uuid4().hex)

        self.access_secret = make_password(self.access_secret)
        super().save(*args, **kwargs)
