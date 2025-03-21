from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from subscriptions.models import *
from subscriptions.serializers import *

# Create your views here.


class SubscribeViewset(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = UserSubscriptionSerializer
    queryset = UserSubscription.objects.filter(is_active=True)

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset
