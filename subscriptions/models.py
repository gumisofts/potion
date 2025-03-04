
from django.db import models
from accounts.models import User, Service

class Subscription(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='subscriptions')
    refund_subscription = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    name = models.CharField(max_length=255)
    frequency = models.BigIntegerField()
    fixed_price = models.BigIntegerField(null=True, blank=True)
    has_fixed_price = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.service.name})"

class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscription'],
                name='unique_user_subscription'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.subscription.name}"