from django.urls import include, path
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

router.register("signed_url", SignUrlViewset, basename="signed-url")

urlpatterns = router.urls + [
    # path("download/<str:stored_as>/", FileDownloadView.as_view(), name="file-download"),
]
