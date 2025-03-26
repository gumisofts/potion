from channels.routing import URLRouter
from django.urls import path
from rest_framework.routers import DefaultRouter

from .consumers import *
from .views import *

router = DefaultRouter()

router.register("register", RegisterViewset, basename="register")
router.register(
    "verifications/confirm", VerificationCodeViewset, basename="users-confirm-code"
)
router.register(
    "verifications/resend", VerificationCodeResendViewset, basename="users-resend-code"
)
router.register("users", UsersViewset, basename="users")
router.register("login", LoginViewset, basename="login")
router.register("register-business", RegisterBusinessViewset, basename="register-business")
router.register("business-detail", BusinessDetailViewset, basename="business-detail")
router.register("business-service", BusinessServiceListViewset, basename="business-service")
router.register("business-service-detail", BusinessServiceDetailViewset, basename="business-service-detail")
# Register Viewsets here
urlpatterns = router.urls + []