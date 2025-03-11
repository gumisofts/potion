from uuid import uuid4

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import (
    EmailValidator,
    FileExtensionValidator,
    RegexValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

phone_validator = RegexValidator(
    regex=r"^(7|9)\d{8}$",
    message="Phone number must be 8-12 digits (e.g., +251945678903).",
)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4)
    username = None
    profile_pic_id = models.UUIDField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=255,
        unique=True,
        validators=[phone_validator],
    )
    is_verified = models.BooleanField(default=False)

    user_type = models.CharField(
        max_length=255, choices=(("user", "user"), ("busines", "bussines"))
    )

    USERNAME_FIELD = "phone_number"

    def __str__(self):
        return self.phone_number


class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    logo_id = models.UUIDField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="businesses")
    wallet = models.OneToOneField(
        "wallets.Wallet", on_delete=models.CASCADE, related_name="business"
    )
    name = models.CharField(max_length=255)
    contact_phone = models.CharField(
        max_length=255, null=True, blank=True, validators=[phone_validator]
    )
    contact_email = models.EmailField(
        validators=[EmailValidator(message="Invalid email format.")]
    )
    license = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    trust_level = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="low",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="services"
    )
    name = models.CharField(max_length=255)
    service_type = models.CharField(
        max_length=20, choices=[("basic", "Basic"), ("premium", "Premium")]
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.service_type})"
