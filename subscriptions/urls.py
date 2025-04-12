from django.urls import path
from rest_framework.routers import DefaultRouter

from subscriptions.views import *

router = DefaultRouter()

router.register("subscribe_service", SubscribeViewsets, basename="subscribe-service")
router.register(
    "unsubscribe_service", UnSubscribeViewsets, basename="unsubscribe-service"
)
router.register("subscriptions", SubscriptionViewset, basename="subscriptions")


urlpatterns = [] + router.urls
