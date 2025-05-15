from django.db import models
from django.utils import timezone

from core.models import BaseModel


class UtilityUser(BaseModel):
    number = models.PositiveBigIntegerField()
    phone_number = models.CharField(max_length=255)


class Utility(BaseModel):
    name = models.CharField(max_length=255)
    image = models.ImageField()


class Billing(BaseModel):
    amount = models.IntegerField(default=10)
    utility = models.ForeignKey(Utility, on_delete=models.CASCADE)
    user = models.ForeignKey(UtilityUser, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    due_date = models.DateTimeField(default=timezone.now)
