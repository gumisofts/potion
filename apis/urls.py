from rest_framework.routers import DefaultRouter

from apis.views import *

router = DefaultRouter()

router.register("keys", ApiKeyViewset, basename="api-key")
urlpatterns = router.urls
