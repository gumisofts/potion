from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager

from subscriptions.dispatch import subscribed, unsubscribed

User = get_user_model()

from core.models import BaseModel


class Subscription(BaseModel):
    name = models.CharField(max_length=255)
    service = models.ForeignKey(
        "accounts.Service", on_delete=models.CASCADE, related_name="subscriptions"
    )
    frequency = models.BigIntegerField()
    fixed_price = models.BigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    has_fixed_price = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.service.name})"


class SubscriptionManager(Manager):

    def subscribe(self, user, subscription, **kwargs):
        sub, created = self.get_or_create(user=user, subscription=subscription)
        sub.is_active = True
        sub.save()

        subscribed.send({"user": user, "subscription": subscription})

        return sub

    def unsubscribe(self, user, subscription, **kwargs):
        sub, created = self.get_or_create(user=user, subscription=subscription)
        sub.is_active = False
        sub.save()
        unsubscribed.send({"user": user, "subscription": subscription})
        return sub


class UserSubscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    next_billing_date = models.DateTimeField(blank=True, null=True)

    objects = SubscriptionManager()

    class Meta:

        unique_together = ["user", "subscription"]

    def __str__(self):
        return f"{self.user.email} - {self.subscription.name}"
