import logging

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification

from .models import Transaction

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transaction)
def update_wallet_balance(sender, instance, **kwargs):
    try:
        if instance.status == "pending":
            from_wallet = instance.from_wallet
            to_wallet = instance.to_wallet
            from_wallet.balance += instance.amount
            to_wallet.balance -= instance.amount
            from_wallet.save()
            to_wallet.save()
            instance.status = "completed"
            instance.save()

        recipient_email = None

        Notification.objects.create(
            title="Transaction Completed",
            content=f"Transfer of amount {instance.amount} ETB has been completed",
            user=instance.from_wallet.user,
        )
        Notification.objects.create(
            title="Transaction Completed",
            content=f"You have received {instance.amount} ETB from {instance.from_wallet.user.phone_number}",
            user=instance.to_wallet.user,
            deliver_method="push",
        )

        # TODO send notifications

        # if instance.wallet.user:
        #     recipient_email = instance.wallet.user.email
        # else:
        #     business = instance.wallet.business_wallets.first()
        #     if business:
        #         recipient_email = business.contact_email

        # if recipient_email:
        #     action = instance.status.capitalize()
        #     email_subject = f"Transaction {action}"
        #     email_message = (
        #         f"Transaction of {instance.amount} ({instance.type}) has been {action}."
        #     )

        #     send_mail(
        #         subject=email_subject,
        #         message=email_message,
        #         from_email="noreply@example.com",
        #         recipient_list=[recipient_email],
        #         fail_silently=False,
        #     )
        #     logger.info(f"Email sent to {recipient_email}")

    except Exception as e:
        logger.error(f"Failed to process transaction {instance.id}: {str(e)}")
