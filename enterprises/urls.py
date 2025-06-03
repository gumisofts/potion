from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()
from .views import *

router.register(r"users/grants", UserGrantViewset, basename="user-grants")
router.register(
    r"enterprises/grants", EnterpriseUserGrantViewset, basename="enterprise-user-grants"
)
router.register(r"access_grants", AccessGrantViewset, basename="access-grants")
router.register(
    r"initiate_payment", PullWalletMoneyViewset, basename="initiate-payment"
)
urlpatterns = router.urls
