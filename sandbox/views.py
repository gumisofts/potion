from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from .serializers import *


class SendMoneyViewset(CreateModelMixin, GenericViewSet):
    serializer_class = SendMoneySerializer
    permission_classes = []


class BankAccountViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = []
    queryset = BankAccount.objects.all()
    lookup_field = "account_number"

    def get_queryset(self):
        queryset = super().get_queryset()
        acc = self.request.query_params.get("acc")
        ins = self.request.query_params.get("ins")
        if acc:
            queryset = queryset.filter(account_number=acc)

        if ins:
            queryset = queryset.filter(institution=ins)

        return queryset

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
