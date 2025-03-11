from uuid import uuid4

from django.db import models


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=255)
    service_id = models.UUIDField()
    frequency = models.BigIntegerField()
    fixed_price = models.BigIntegerField(null=True, blank=True)
    has_fixed_price = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.service.name})"


class UserSubscription(models.Model):
    user_id = models.UUIDField()
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscription"], name="unique_user_subscription"
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.subscription.name}"
