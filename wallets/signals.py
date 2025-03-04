
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Transaction
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Transaction, dispatch_uid='update_wallet_balance_id')
def update_wallet_balance(sender, instance, **kwargs):
    try:
        if instance.status == 'completed':
            wallet = instance.wallet
            if instance.type == 'credit':
                wallet.balance += instance.amount
            elif instance.type == 'debit':
                wallet.balance -= instance.amount
            wallet.save()
            logger.info(f"Wallet {wallet.id} balance updated to {wallet.balance}")

        recipient_email = None
        if instance.wallet.user:
            recipient_email = instance.wallet.user.email
        else:
            business = instance.wallet.business_wallets.first()
            if business:
                recipient_email = business.contact_email
        
        if recipient_email:
            action = instance.status.capitalize()
            email_subject = f"Transaction {action}"
            email_message = f"Transaction of {instance.amount} ({instance.type}) has been {action}."
            
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email='noreply@example.com',
                recipient_list=[recipient_email],
                fail_silently=False
            )
            logger.info(f"Email sent to {recipient_email}")

    except Exception as e:
        logger.error(f"Failed to process transaction {instance.id}: {str(e)}")