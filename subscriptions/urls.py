from django.urls import path
from rest_framework.routers import DefaultRouter

from subscriptions.views import *

router = DefaultRouter()

router.register("subscribe", SubscribeViewset, basename="subscribe")
router.register("subscriptions", SubscriptionViewset, basename="subscriptions")


urlpatterns = [] + router.urls
