from django.urls import path
from rest_framework.routers import DefaultRouter

from wallets.views import *

router = DefaultRouter()

router.register("wallets", WalletViewsets)

<<<<<<< HEAD
router.register("wallet-transaction-fund", TransactionWalletViewsets, basename="wallet_transaction_fund_api_view")

=======
>>>>>>> dev-v01
urlpatterns = router.urls + []
