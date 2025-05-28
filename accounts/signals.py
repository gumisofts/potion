import logging
from datetime import datetime, timedelta

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.utils import *
from wallets.models import Wallet

from .dispatch import *
from .models import Business, TemporaryCode, User, VerificationCode
from django.utils import timezone

logger = logging.getLogger(__name__)


@receiver(user_phone_verified, sender=User, dispatch_uid="create_user_wallet_id")
def create_user_wallet(sender, instance, **kwargs):
    wallet = Wallet.objects.create(user_id=instance.id)
    logger.info(f"Wallet created for user: {instance.email}")


@receiver(post_save, sender=Business)
def create_business_wallet(sender, instance, created, **kwargs):
    if created:
        wallet = Wallet.objects.create(business=instance)
        logger.info(f"Wallet created for business: {instance.name}")
    else:
        logger.info(f"Signal received for business update: {instance.name}")


@receiver(user_registered, sender=User)
def upon_registration(sender, instance, method, **kwargs):


    code = str(generate_secure_six_digits())

    if method == "EMAIL":

        VerificationCode.objects.create(
            user=instance,
            token=code,
            expires_at=timezone.now() + timedelta(minutes=5),
            code_type=2,
        )

    else:
        VerificationCode.objects.create(
            user=instance,
            token=code,
            expires_at=timezone.now() + timedelta(minutes=5),
            code_type=1,
        )
        TemporaryCode.objects.create(phone_number=instance.phone_number, code=code)
