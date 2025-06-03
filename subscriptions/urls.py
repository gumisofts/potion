from django.urls import path
from rest_framework.routers import DefaultRouter

from subscriptions.views import *

router = DefaultRouter()

router.register("subscribe_service", SubscribeViewsets, basename="subscribe-service")
router.register(
    "unsubscribe_service", UnSubscribeViewsets, basename="unsubscribe-service"
)
router.register(
    "user_subscriptions", UserSubscriptionViewset, basename="user-subscriptions"
)
router.register("subscriptions", SubscriptionViewset, basename="subscriptions")

router.register(
    r"popular_subscriptions",
    PopularSubscriptionViewset,
    basename="popular-subscriptions",
)
urlpatterns = [] + router.urls
