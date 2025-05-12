from rest_framework.routers import DefaultRouter

from bills.views import *

router = DefaultRouter()

router.register(r"pay_bills", PaybillsViewset, basename="pay-bills")
router.register(r"unpaid", BillsViewset, basename="unpaid-bills")

urlpatterns = router.urls
