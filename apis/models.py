from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Create your models here.
class ApiKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    label = models.CharField(max_length=255, default="default")
    hashed_key = models.CharField(max_length=255, unique=True)
    business = models.ForeignKey(
        "accounts.Business", on_delete=models.CASCADE, related_name="keys"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="keys")
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("business", "label")]
