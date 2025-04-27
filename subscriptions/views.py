from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from subscriptions.models import *
from subscriptions.serializers import *

# Create your views here.


class SubscribeViewsets(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = UserSubscriptionSerializer
    queryset = UserSubscription.objects.all()

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="subscription_id",
                type=OpenApiTypes.INT,
                description="Subscription ID",
                required=False,
            ),
            OpenApiParameter(
                name="next_billing_date_gt",
                type=OpenApiTypes.DATETIME,
                description="next billing date greater than",
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UnSubscribeViewsets(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = UnsubscribeSerializer
    queryset = UserSubscription.objects.filter(is_active=False)

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SubscriptionViewset(ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.filter(is_active=True)

    def get_queryset(self):
        return super().get_queryset()
