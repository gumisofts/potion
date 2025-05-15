from django.db.models.signals import post_save
from django.dispatch import receiver

from enterprises.models import *
from notifications.firebase import send_push_notification


@receiver(post_save, sender=UserGrant)
def on_grant_created(sender, instance: UserGrant, created, **kwargs):
    for device in instance.user.devices.all():
        send_push_notification(
            device.id,
            f"{instance.enterprise.long_name} is requesting access to your wallet",
            f"limit {instance.max_amount}",
        )
