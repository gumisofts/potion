
from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from wallets.models import Transaction

from datetime import datetime
from django.utils import timezone
from django.core.validators import MinValueValidator

from django.core.validators import RegexValidator

phone_regex = r"^(\+)?(?P<country_code>251)?(?P<phone_number>[79]\d{8})$"
phone_validator = RegexValidator(
    regex=phone_regex,
    message="Phone number must start with +2519, 2519, 9, +2517, 2517, or 7 followed by 8 digits.",
)


class Dispute(BaseModel):
    DISPUTE_STATUS = [
        ('needs_response', 'Needs Response'),
        ('in_review', 'In Review'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        related_name='disputes',
        help_text='The transaction being disputed'
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[phone_validator],
        help_text='Phone number of the reporter'
    )
    amount = models.BigIntegerField(
        validators=[MinValueValidator(0, message="Dispute amount.")],
        help_text='Disputed amount in ETB'
    )
    status = models.CharField(
        max_length=20,
        choices=DISPUTE_STATUS,
        default='needs_response',
        help_text='Current status of the dispute'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about the dispute'
    )
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the dispute was resolved'
    )
    refund_transaction = models.OneToOneField(
        'wallets.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispute_refund',
        help_text='The refund transaction created for this dispute'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Dispute')
        verbose_name_plural = _('Disputes')

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        if self.transaction_id and not self.amount:
            self.amount = self.transaction.amount
            
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

