import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from wallets.models import Wallet

from .models import Business, User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User, dispatch_uid="create_user_wallet_id")
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        wallet = Wallet.objects.create(user=instance)
        instance.wallet = wallet
        instance.save()
        logger.info(f"Wallet created for user: {instance.email}")
    else:
        logger.info(f"Signal received for user update: {instance.email}")


@receiver(post_save, sender=Business, dispatch_uid="create_business_wallet_id")
def create_business_wallet(sender, instance, created, **kwargs):
    if created:
        wallet = Wallet.objects.create()
        instance.wallet = wallet
        instance.save()
        logger.info(f"Wallet created for business: {instance.name}")
    else:
        logger.info(f"Signal received for business update: {instance.name}")
