from django.urls import path
from rest_framework.routers import DefaultRouter

from subscriptions.views import *

router = DefaultRouter()

router.register(
    "service_subscriptions", SubscribeViewset, basename="service-subscriptions"
)
router.register("subscriptions", SubscriptionViewset, basename="subscriptions")


urlpatterns = [] + router.urls
