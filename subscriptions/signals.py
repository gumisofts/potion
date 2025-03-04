
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Subscription
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Subscription, dispatch_uid='notify_subscription_id')
def notify_subscription_update(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    
    try:
        if instance.service and instance.service.business and instance.service.business.owner:
            email = instance.service.business.owner.email
            email_subject = f"Subscription {action}"
            email_message = f"Subscription '{instance.name}' for service '{instance.service.name}' has been {action}."
            
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email='noreply@example.com',
                recipient_list=[email],
                fail_silently=False
            )
            logger.info(f"Email sent to {email} for subscription {instance.name}")
        else:
            logger.error("Missing relationships for subscription notification")
    
    except Exception as e:
        logger.error(f"Failed to send subscription email: {str(e)}")