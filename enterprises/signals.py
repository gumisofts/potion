import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from enterprises.models import *
from notifications.firebase import send_push_notification
from wallets.models import Wallet

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserGrant)
def on_grant_created(sender, instance: UserGrant, created, **kwargs):
    for device in instance.user.devices.all():
        send_push_notification(
            device.id,
            f"{instance.enterprise.long_name} is requesting access to your wallet",
            f"limit {instance.max_amount}",
        )


@receiver(post_save, sender=Enterprise)
def create_business_wallet(sender, instance, created, **kwargs):
    if created:
        wallet = Wallet.objects.create(enterprise=instance)
        logger.info(f"Wallet created for enterprise: {instance.name}")
    else:
        logger.info(f"Signal received for enterprise update: {instance.name}")
