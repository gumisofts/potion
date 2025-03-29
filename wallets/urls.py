from django.urls import path
from rest_framework.routers import DefaultRouter

from wallets.views import *

router = DefaultRouter()

router.register("wallets", WalletViewsets)

urlpatterns = router.urls + []
