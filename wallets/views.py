from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from wallets.models import Wallet
from wallets.serializers import *


class WalletViewsets(RetrieveModelMixin, GenericViewSet):
    serializer_class = WalletSerializers
    queryset = Wallet.objects.filter(is_restricted=False)

    def get_queryset(self):
        return super().get_queryset()


class SendMoneyP2PViewset(CreateModelMixin, GenericViewSet):
    serializer_class = None


class SendMoneyExternalViewset(CreateModelMixin, GenericViewSet):
    serializer_class = None
