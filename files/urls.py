from django.urls import include, path
from rest_framework import routers

from .views import FileDownloadView, GenerateSignedUrlView

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("upload_url/", GenerateSignedUrlView.as_view(), name="signed-url"),
    path("download/<str:stored_as>/", FileDownloadView.as_view(), name="file-download"),
]
