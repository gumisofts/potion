from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import Permission
from django.db import models

from core.models import BaseModel

User = get_user_model()


class Enterprise(BaseModel):
    long_name = models.CharField(max_length=255, verbose_name="Long Name")
    short_name = models.CharField(max_length=255, verbose_name="Short Name")
    description = models.TextField(verbose_name="Description")
    logo = models.ImageField(upload_to="enterprises/logos", verbose_name="Logo")
    is_active = models.BooleanField(default=False)
    pull_limit = models.IntegerField(default=0, verbose_name="Pull Limit")
    actions_call_back = models.URLField(
        max_length=255, null=True, blank=True, verbose_name="Actions Call Back"
    )


class UserGrant(BaseModel):

    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expires At")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_grants",
        verbose_name="User",
    )
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="user_grants",
        verbose_name="Enterprise",
    )
    max_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Max Amount"
    )

    meta_data = models.JSONField(
        verbose_name="Meta Data", null=True, blank=True
    )  # {"purpose": "Monthly subscription", "referenceId": "sub-789"}

    grant_status = models.CharField(
        max_length=255,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("suspended", "Suspended"),
        ],
        default="pending",
        verbose_name="Grant Status",
    )
    is_active = models.BooleanField(default=False, verbose_name="Is Active")

    def __str__(self):
        return f"{self.user.username} - {self.enterprise.long_name}"


class AccessGrant(BaseModel):
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="wallets",
        verbose_name="Enterprise",
    )

    access_id = models.CharField(max_length=255, verbose_name="Access ID")
    access_secret = models.CharField(max_length=255, verbose_name="Access Secret")
    is_active = models.BooleanField(default=False, verbose_name="Is Active")

    def save(self, *args, **kwargs):
        self.access_secret = make_password(self.access_secret)
        return super().save(*args, **kwargs)


class Settlement(BaseModel):
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="settlements",
        verbose_name="Enterprise",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    is_settled = models.BooleanField(default=False, verbose_name="Is Settled")
