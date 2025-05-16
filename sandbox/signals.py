from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *


@receiver(post_save, sender=Institution)
def on_institution_created(sender, instance, created, **kwargs):

    if created:
        InstitutionWallet.objects.create(balance=0, institution=instance)
