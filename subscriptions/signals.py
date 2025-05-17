import logging

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from wallets.models import Transaction

from .models import Subscription, UserSubscription

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserSubscription)
def deduct_from_user_wallet(sender, instance: UserSubscription, created, **kwargs):
    if created:
        # Create transaction here
        try:
            # Assuming you have a function to create a transaction
            # create_transaction(instance)
            Transaction.objects.create(
                from_wallet=instance.user.wallet,
                to_wallet=instance.subscription.service.business.wallet,
                amount=instance.subscription.fixed_price,
                remarks=f"Payment for subscription {instance.subscription.name}",
                status="pending",
            )
        except Exception as e:
            logger.error(
                f"Failed to create transaction for subscription {instance.id}: {str(e)}"
            )
            return
