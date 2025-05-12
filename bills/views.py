from django.db.models import Sum
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from bills.models import *
from bills.serializers import *


class UtilityViewset(CreateModelMixin, GenericViewSet):
    serializer_class = None
    queryset = None


class PaybillsViewset(CreateModelMixin, GenericViewSet):
    serializer_class = PayUtilitySerializer


class BillsViewset(RetrieveModelMixin, GenericViewSet):
    serializer_class = None
    queryset = None

    lookup_field = "user__number"

    def retrieve(self, request, user__number, *args, **kwargs):

        queryset = Billing.objects.filter(
            user__number=user__number, is_paid=False, due_date__lte=timezone.now()
        )

        total = queryset.aggregate(total=Sum("amount")).get("total")

        total = 0 if total is None else total

        return Response({"amount": total})
