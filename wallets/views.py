from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from wallets.models import Wallet
from wallets.serializers import *


class WalletViewsets(RetrieveModelMixin, GenericViewSet):
    serializer_class = WalletSerializers
    queryset = Wallet.objects.filter(is_restricted=False)

    def get_queryset(self):
        return super().get_queryset()


class TransactionViewsets(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TransactionSerializer
    permission_classes = []
    queryset = Transaction.objects.all()


class SendMoneyP2PViewsets(CreateModelMixin, GenericViewSet):
    serializer_class = SendMoneyP2PSerializer
    permission_classes = []


class SendMoneyExternalViewsets(CreateModelMixin, GenericViewSet):
    serializer_class = None
