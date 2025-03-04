
from django.urls import path
from .views import Home, RegisterView
from channels.routing import URLRouter
from rest_framework.routers import DefaultRouter
from .consumers import *

router = DefaultRouter()
# Register Viewsets here


urlpatterns = router.urls + [
    path('home/', Home.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
]

auth_router = URLRouter([path("test/", TestConsumer.as_asgi())])
