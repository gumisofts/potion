import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .dispatch import *

from wallets.models import Wallet
from datetime import datetime, timedelta
from .models import Business, User, TemporaryCode, VerificationCode
from core.utils import *

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User, dispatch_uid="create_user_wallet_id")
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        wallet = Wallet.objects.create(user_id=instance.id)
        logger.info(f"Wallet created for user: {instance.email}")
    else:
        logger.info(f"Signal received for user update: {instance.email}")


@receiver(pre_save, sender=Business, dispatch_uid="create_business_wallet_id")
def create_business_wallet(sender, instance, created, **kwargs):
    if created:
        wallet = Wallet.objects.create(user_id=instance.owner.id)
        instance.wallet_id = wallet.id
        logger.info(f"Wallet created for business: {instance.name}")
    else:
        logger.info(f"Signal received for business update: {instance.name}")


@receiver(user_registered, sender=User)
def upon_registration(sender, instance, method, **kwargs):

    print("Generating Verification Codes...")
    print(kwargs)

    code = str(generate_secure_six_digits())

    if method == "EMAIL":

        VerificationCode.objects.create(
            user=instance,
            token=code,
            expires_at=datetime.now() + timedelta(minutes=5),
            code_type=2,
        )

    else:
        VerificationCode.objects.create(
            user=instance,
            token=code,
            expires_at=datetime.now() + timedelta(minutes=5),
            code_type=1,
        )
        TemporaryCode.objects.create(code=code, phone_number=instance.phone_number)
