from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models

from core.models import BaseModel

User = get_user_model()


class Notification(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    groups = models.ManyToManyField(Group, blank=True, related_name="notifications")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=255,
        choices=[("broadcast", "broadcast"), ("dedicated", "dedicated")],
        default="broadcast",
    )

    delivery_method = models.CharField(
        max_length=255, choices=[("inApp", "inApp"), ("push", "push")], default="inApp"
    )
