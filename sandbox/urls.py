from django.urls import path
from rest_framework.routers import DefaultRouter

from sandbox.views import *

router = DefaultRouter()

router.register(r"send_money", SendMoneyViewset, basename="send-money")
router.register(r"bank_accounts", BankAccountViewset, basename="bank-accounts")


urlpatterns = router.urls
