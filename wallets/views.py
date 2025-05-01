from django.db.models import Q
from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from wallets.models import Wallet
from wallets.serializers import *


class WalletViewsets(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = WalletSerializers
    queryset = Wallet.objects.filter(is_restricted=False)
    permission_classes = []
    lookup_field = "user__id"


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
    permission_classes = []


class SendMoneyExternalViewsets(CreateModelMixin, GenericViewSet):
    serializer_class = None
