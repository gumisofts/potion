from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()


router.register(r"notifications", NotificationViewset, basename="notifications")

urlpatterns = router.urls
