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
        subscription_id = self.request.query_params.get("subscription_id")
        next_billing_date_gt = self.request.query_params.get("next_billing_date_gt")
        next_billing_date_lt = self.request.query_params.get("next_billing_date_lt")
        if subscription_id:
            queryset = queryset.filter(subscription=subscription_id)
        if next_billing_date_gt:
            queryset = queryset.filter(next_billing_date__gt=next_billing_date_gt)
        if next_billing_date_lt:
            queryset = queryset.filter(next_billing_date__lt=next_billing_date_lt)

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
            OpenApiParameter(
                name="next_billing_date_lt",
                type=OpenApiTypes.DATETIME,
                description="next billing date less than",
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
        queryset = super().get_queryset()

        service_id = self.request.query_params.get("service_id")
        business_id = self.request.query_params.get("business_id")
        service_type = self.request.query_params.get("service_type")

        if service_id:
            queryset = queryset.filter(service=service_id)

        if business_id:
            queryset = queryset.filter(service__business=business_id)

        if service_type:
            queryset = queryset.filter(service_type=service_type)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="service_id",
                required=False,
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.UUID,
            ),
            OpenApiParameter(
                name="business_id",
                required=False,
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.UUID,
            ),
            OpenApiParameter(
                name="service_type",
                required=False,
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserSubscriptionViewset(ListModelMixin, GenericViewSet):
    serializer_class = UserSubscriptionSerializer
    queryset = UserSubscription.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="is_active", required=False, type=OpenApiTypes.BOOL),
            OpenApiParameter(
                name="next_billing_date_gt",
                type=OpenApiTypes.DATETIME,
                description="next billing date greater than",
                required=False,
            ),
            OpenApiParameter(
                name="next_billing_date_lt",
                type=OpenApiTypes.DATETIME,
                description="next billing date less than",
                required=False,
            ),
            OpenApiParameter(
                name="subscription_id",
                type=OpenApiTypes.INT,
                description="Subscription ID",
                required=False,
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.UUID,
                description="User ID",
                required=False,
            ),
            OpenApiParameter(
                name="service_id",
                type=OpenApiTypes.UUID,
                description="Service ID",
                required=False,
            ),
            OpenApiParameter(
                name="business_id",
                type=OpenApiTypes.UUID,
                description="Business ID",
                required=False,
            ),
            OpenApiParameter(
                name="service_type",
                type=OpenApiTypes.STR,
                description="Service Type",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        is_active = self.request.query_params.get("is_active", None)

        if is_active and is_active in ["True", "False"]:
            queryset = queryset.filter(is_active=is_active)

        queryset = queryset.filter(user=self.request.user)
        next_billing_date_gt = self.request.query_params.get("next_billing_date_gt")
        next_billing_date_lt = self.request.query_params.get("next_billing_date_lt")
        subscription_id = self.request.query_params.get("subscription_id")
        user_id = self.request.query_params.get("user_id")
        service_id = self.request.query_params.get("service_id")
        business_id = self.request.query_params.get("business_id")
        service_type = self.request.query_params.get("service_type")
        if next_billing_date_gt:
            queryset = queryset.filter(next_billing_date__gt=next_billing_date_gt)
        if next_billing_date_lt:
            queryset = queryset.filter(next_billing_date__lt=next_billing_date_lt)
        if subscription_id:
            queryset = queryset.filter(subscription=subscription_id)
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        if service_id:
            queryset = queryset.filter(subscription__service=service_id)
        if business_id:
            queryset = queryset.filter(subscription__service__business=business_id)
        if service_type:
            queryset = queryset.filter(subscription__service_type=service_type)

        return queryset
