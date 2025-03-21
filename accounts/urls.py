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
# Register Viewsets here
urlpatterns = router.urls + [
    # path(
    #     "send-confirmation-email/",
    #     SendEmailConfirmationTokenAPIView.as_view(),
    #     name="send_email_confirmation_api_view",
    # ),
    # path("confirm-email/", confirm_email_view, name="confirm_email_view"),
]
