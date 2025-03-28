from django.urls import path
from rest_framework.routers import DefaultRouter

from wallets.views import *

router = DefaultRouter()

router.register("wallets", WalletViewsets)

router.register("wallet-transaction-fund", TransactionWalletViewsets, basename="wallet_transaction_fund_api_view")

urlpatterns = router.urls + []
