import logging

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification

from .models import Transaction

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transaction)
def update_wallet_balance(sender, instance, created, **kwargs):

    if created:
        try:
            if instance.status == "pending" and instance.from_wallet:
                from_wallet = instance.from_wallet
                from_wallet.balance -= instance.amount
                from_wallet.save()
                Notification.objects.create(
                    title="Transaction Completed",
                    content=f"Transfer of amount {instance.amount} ETB has been completed",
                    user=instance.from_wallet.user,
                    delivery_method="push",
                    transaction_id=instance.id,
                )
            if instance.status == "pending" and instance.to_wallet:
                to_wallet = instance.to_wallet
                to_wallet.balance += instance.amount
                to_wallet.save()
                from_name = (
                    instance.from_wallet.user.first_name if instance.from_wallet else ""
                )
                Notification.objects.create(
                    title="Payment Received",
                    content=f"You have received {instance.amount} ETB from {from_name}",
                    user=instance.to_wallet.user,
                    delivery_method="push",
                    transaction_id=instance.id,
                )

            instance.status = "completed"
            instance.save()

        except Exception as e:
            logger.error(f"Failed to process transaction {instance.id}: {str(e)}")
