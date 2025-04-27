from django.db import models

from core.models import BaseModel
from django.contrib.auth.models import Permission


class Enterprise(BaseModel):
    long_name = models.CharField(max_length=255, verbose_name="Long Name")
    short_name = models.CharField(max_length=255, verbose_name="Short Name")
    description = models.TextField(verbose_name="Description")
    logo = models.ImageField(upload_to="enterprises/logos", verbose_name="Logo")
    is_active = models.BooleanField(default=False)

    pull_limit = models.IntegerField(default=0, verbose_name="Pull Limit")


class ApiKey(BaseModel):
    key = models.CharField(max_length=255, unique=True, verbose_name="API Key")
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name="Enterprise",
    )

    permissions = models.ManyToManyField(Permission, verbose_name="Permissions")

    restricted = models.BooleanField(default=False, verbose_name="Restricted")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expires At")

    actions_call_back = models.URLField(
        max_length=255, null=True, blank=True, verbose_name="Actions Call Back"
    )


class WalletGrant(BaseModel):
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="wallets",
        verbose_name="Enterprise",
    )
    client_id = models.CharField(max_length=255, verbose_name="Client ID")
    client_secret = models.CharField(max_length=255, verbose_name="Client Secret")
    redirect_uri = models.URLField(max_length=255, verbose_name="Redirect URI")
    scope = models.TextField(verbose_name="Scope", null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Is Active")


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
