from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()
from .views import *

router.register(r"users/grants", UserGrantViewset, basename="user-grants")
router.register(r"access_grants", AccessGrantViewset, basename="access-grants")
urlpatterns = router.urls
