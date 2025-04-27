from channels.routing import URLRouter
from django.urls import path
from rest_framework.routers import DefaultRouter

from .consumers import *
from .views import *

router = DefaultRouter()

router.register("register", RegisterViewset, basename="register")
router.register("users/devices", UserDeviceViewset, basename="user-devices")
router.register(
    "verifications/confirm", VerificationCodeViewset, basename="users-confirm-code"
)
router.register("business", BusinessViewset, basename="business")
router.register(
    "services/categories", CategoriesViewset, basename="services-categories"
)
router.register("services", BusinessServiceViewset, basename="business-services")
router.register(
    "verifications/resend", VerificationCodeResendViewset, basename="users-resend-code"
)
router.register("users", UsersViewset, basename="users")
router.register("login", LoginViewset, basename="login")
# Register Viewsets here
urlpatterns = router.urls + []
