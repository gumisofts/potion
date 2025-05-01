from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models, transaction

from accounts.models import Business, User


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    business = models.OneToOneField(
        Business, on_delete=models.PROTECT, null=True, blank=True, related_name="wallet"
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

    def __str__(self):
        return f"Wallet ({self.user.email if self.user else 'Business'})"

    def __str__(self):
        return f"Wallet({self.user})"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    from_wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} (Status: {self.status})"
