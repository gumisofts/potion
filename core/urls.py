from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("files/", include("files.urls")),
    path("notifications/", include("notifications.urls")),
    path("bills/", include("bills.urls")),
    path("sandbox/", include("sandbox.urls")),
    path("accounts/", include("accounts.urls")),
    path("wallets/", include("wallets.urls")),
    path("subscriptions/", include("subscriptions.urls")),
    path("apis/enterprises/", include("enterprises.urls")),
    path("platform_admin/", include("platform_admin.urls")),
]
