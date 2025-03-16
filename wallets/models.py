from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models, transaction

from accounts.models import User, Business


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    business = models.OneToOneField(
        Business, on_delete=models.PROTECT, null=True, blank=True
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

    @transaction.atomic
    def update_balance(self, amount, transaction_type):
        """
        Safely updates the wallet balance using row-level locking.
        """
        wallet = Wallet.objects.select_for_update().get(id=self.id)

        if transaction_type == "credit":
            wallet.balance += amount
        elif transaction_type == "debit":
            if wallet.balance < amount:
                raise ValueError("Insufficient balance for debit transaction.")
            wallet.balance -= amount
        else:
            raise ValueError("Invalid transaction type.")

        wallet.save()


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    type = models.CharField(
        max_length=10, choices=[("credit", "Credit"), ("debit", "Debit")]
    )
    amount = models.BigIntegerField(
        validators=[MinValueValidator(1, message="Amount must be at least 1.")]
    )
    notes = models.TextField(null=True, blank=True)
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
        return f"{self.type} of {self.amount} (Status: {self.status})"

    def save(self, *args, **kwargs):
        """
        Override save method to update wallet balance safely.
        """
        if self.status == "completed":
            with transaction.atomic():
                self.wallet.update_balance(self.amount, self.type)
        super().save(*args, **kwargs)
