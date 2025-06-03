from django.urls import path
from rest_framework.routers import DefaultRouter

from wallets.views import *

router = DefaultRouter()

router.register("wallets/public", WalletPublicViewset, basename="wallets-public")
router.register("wallets", WalletViewsets)
router.register("business/wallets", WalletViewsetBusiness, basename="business-wallets")
router.register("transactions", TransactionViewsets, basename="transactions")
router.register("send/p2p", SendMoneyP2PViewsets, basename="send-p2p")
router.register("send/external", SendMoneyExternalViewsets, basename="send-external")
router.register(
    "receive/external", ReceiveMoneyExternalViewsets, basename="receive-money-external"
)
router.register("snapshots", WalletDailySnapshotViewset, basename="wallet-snapshots")
urlpatterns = router.urls + [
    path("stats/transactions/<tr_id>", TransactionStats.as_view(), name="")
]
