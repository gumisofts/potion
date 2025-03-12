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
    def upload_to(self, filename):
        return filename

    wallet = models.OneToOneField(
        "wallets.Wallet",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_wallet",
    )
    profile_pic = models.ImageField(
        upload_to=upload_to,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                [
                    "jpg",
                    "png",
                    "jpeg",
                    "heic",
                ]
            )
        ],
    )
    phone_number = models.CharField(
        max_length=255,
        unique=True,
        validators=[phone_validator],
    )
    is_verified = models.BooleanField(default=False)
    is_email_confirmed = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"

    # REQUIRED_FIELDS = ["first_name"]
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.phone_number
    
class EmailConfirmationToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Business(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="businesses")
    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="business_wallets",
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
        default="medium",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Service(models.Model):
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
