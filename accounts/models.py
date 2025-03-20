from uuid import uuid4

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import (
    EmailValidator,
    FileExtensionValidator,
    RegexValidator,
)
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from core.utils import hash256

phone_validator = RegexValidator(
    regex=r"^(7|9)\d{8}$",
    message="Phone number must be 8-12 digits (e.g., 945678903).",
)


class UserManager(BaseUserManager):
    def create(
        self,
        phone_number,
        first_name,
        last_name=None,
        is_active=True,
        is_superuser=False,
        is_staff=False,
        **kwargs,
    ):
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_superuser=is_superuser,
            is_staff=is_staff,
            **kwargs,
        )

        user.save()

        return user

    def create_superuser(
        self,
        phone_number,
        first_name,
        last_name=None,
        is_active=True,
        **kwargs,
    ):
        user = self.create(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_superuser=True,
            is_staff=True,
            **kwargs,
        )
        user.is_phone_verified = True
        user.is_email_verified = True

        user.save()

        return user


class User(AbstractUser):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid4)
    profile_pic_id = models.UUIDField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=255,
        unique=True,
        validators=[phone_validator],
    )
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)

    user_type = models.CharField(
        max_length=255, choices=(("user", "user"), ("busines", "bussines"))
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()

    def __str__(self):
        return self.phone_number


class EmailConfirmationToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    logo_id = models.UUIDField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="businesses")
    name = models.CharField(max_length=255)
    contact_phone = models.CharField(
        max_length=255, null=True, blank=True, validators=[phone_validator]
    )
    contact_email = models.EmailField(
        validators=[EmailValidator(message="Invalid email format.")]
    )
    license_id = models.UUIDField(max_length=255)
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


class VerificationCode(models.Model):
    token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="codes")
    created_at = models.DateTimeField(auto_now_add=True)
    code_type = models.IntegerField(choices=[(1, "PHONE"), (2, "EMAIL")], default=1)
    is_used = models.BooleanField(default=True)

    def save(self, *args, **kwargs):

        self.token = hash256(self.token)

        return super().save(*args, **kwargs)


class TemporaryCode(models.Model):
    phone_number = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
