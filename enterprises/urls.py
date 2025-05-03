from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()
from .views import *

router.register(r"users/grants", UserGrantViewset, basename="user-grants")
urlpatterns = router.urls
