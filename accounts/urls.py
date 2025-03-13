from channels.routing import URLRouter
from django.urls import path
from rest_framework.routers import DefaultRouter

from .consumers import *
from .views import (
    Home,
    RegisterView,
    SendEmailConfirmationTokenAPIView,
    UserInformationAPIView,
    confirm_email_view,
)

router = DefaultRouter()
# Register Viewsets here

app_name = "users"

urlpatterns = router.urls + [
    path("api/home/", Home.as_view(), name="home"),
    path("api/register/", RegisterView.as_view(), name="register_api_view"),
    path(
        "api/userinfo/",
        UserInformationAPIView.as_view(),
        name="user_information_api_view",
    ),
    path(
        "api/send-confirmation-email/",
        SendEmailConfirmationTokenAPIView.as_view(),
        name="send_email_confirmation_api_view",
    ),
    path("accounts/confirm-email/", confirm_email_view, name="confirm_email_view"),
]

auth_router = URLRouter([path("test/", TestConsumer.as_asgi())])
