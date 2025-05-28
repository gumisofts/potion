from django.db.models import Q
from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from wallets.models import Wallet
from wallets.permissions import *
from wallets.serializers import *


class WalletViewsets(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = WalletSerializers
    queryset = Wallet.objects.filter(is_restricted=False, business=None)
    permission_classes = [IsWalletOwner]
    lookup_field = "user__id"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show user's own wallet
        queryset = queryset.filter(user=self.request.user)

        user_id = self.request.query_params.get("user_id")
        phone_number = self.request.query_params.get("phone_number")

        if user_id:
            queryset = queryset.filter(user=user_id)
        if phone_number:
            queryset = queryset.filter(user__phone_number=phone_number)

        return queryset

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            self.permission_denied(self.request, message="Wallet not found")
        return obj


class WalletPublicViewset(ListModelMixin, GenericViewSet):
    serializer_class = WalletPublicSerializer
    queryset = Wallet.objects.filter(is_restricted=False)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        phone_number = self.request.query_params.get("phone_number")

        if user_id:
            queryset = queryset.filter(user=user_id)
        if phone_number:
            queryset = queryset.filter(user__phone_number=phone_number)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="phone_number", required=False, type=OpenApiTypes.STR
            ),
            OpenApiParameter(name="user_id", required=False, type=OpenApiTypes.STR),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TransactionViewsets(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TransactionSerializer
    permission_classes = []
    queryset = Transaction.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        wallet = self.request.query_params.get("wallet")

        if wallet:
            queryset = queryset.filter(Q(from_wallet=wallet) | Q(to_wallet=wallet))

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="wallet", required=False, type=OpenApiTypes.UUID)
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SendMoneyP2PViewsets(CreateModelMixin, GenericViewSet):
    serializer_class = SendMoneyP2PSerializer
    permission_classes = [IsAuthenticated]


class SendMoneyExternalViewsets(CreateModelMixin, GenericViewSet):
    serializer_class = None


class ReceiveMoneyExternalViewsets(CreateModelMixin, GenericViewSet):
    serializer_class = ReceiveMoneyExternalSerializer
    permission_classes = [ExternalSysPermission]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="X-Access-Id",
                type=OpenApiTypes.STR,
                required=True,
                location=OpenApiParameter.HEADER,
            ),
            OpenApiParameter(
                name="X-Access-Secret",
                type=OpenApiTypes.STR,
                required=True,
                location=OpenApiParameter.HEADER,
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
