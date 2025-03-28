from django.shortcuts import render
<<<<<<< Updated upstream

# Create your views here.
=======
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

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


class TransactionWalletViewsets(GenericViewSet, UpdateModelMixin, RetrieveModelMixin, ListModelMixin, CreateModelMixin):
    queryset = Transaction.objects.all()
    serializer_class = TransactionWalletSerializer
>>>>>>> Stashed changes
