from channels.routing import URLRouter
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register("all_users", UsersDataViewset, basename="all-users-data")
router.register(
    r"transaction-records", TransactionRecordViewset, basename="transaction-records"
)

router.register("admin_platform_login", LoginViewset, basename="admin-platform-login")
# Register Viewsets here
urlpatterns = router.urls + []
