from django.urls import path
from rest_framework.routers import DefaultRouter

from wallets.views import *

router = DefaultRouter()

router.register("wallets", WalletViewsets)
router.register("transactions", TransactionViewsets, basename="transactions")
router.register("send/p2p", SendMoneyP2PViewsets, basename="send-p2p")

urlpatterns = router.urls + []
