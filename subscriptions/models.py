from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager

from subscriptions.dispatch import subscribed, unsubscribed

User = get_user_model()


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=255)
    service = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    frequency = models.BigIntegerField()
    fixed_price = models.BigIntegerField(null=True, blank=True)
    has_fixed_price = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.service.name})"


class SubscriptionManager(Manager):

    def subscribe(self, user, subscription):
        sub = self.get_or_create(user=user, subscription=subscription)
        sub.is_active = True
        sub.save()

        subscribed.send(self.__class__, user, subscription)

        return sub

    def unsubscribe(self, user, subscription):
        sub = self.get_or_create(user=user, subscription=subscription)
        sub.is_active = False
        sub.save()
        unsubscribed.send(self.__class__, user, subscription)
        return sub


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SubscriptionManager()

    class Meta:

        unique_together = ["user", "subscription"]

    def __str__(self):
        return f"{self.user.email} - {self.subscription.name}"
