from django.db.models.signals import post_save
from django.dispatch import receiver

from .firebase import *
from .models import Notification


@receiver(post_save, sender=Notification)
def on_notification_created(sender, instance: Notification, created, **kwargs):

    if instance.user:
        for device in instance.user.devices.all():
            if instance.delivery_method == "push":
                tt = send_push_notification(
                    device.id, title=instance.title, body=instance.content
                )
                print(tt)
