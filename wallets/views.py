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
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from rest_framework.views import APIView
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from collections import defaultdict
import calendar


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


class WalletViewsetBusiness(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = WalletSerializers
    queryset = Wallet.objects.filter(is_restricted=False, user=None)
    lookup_field = "business__id"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show business wallets
        queryset = queryset.filter(business__in=self.request.user.businesses.all())
        user_id = self.request.query_params.get("user_id")
        phone_number = self.request.query_params.get("phone_number")
        if user_id:
            queryset = queryset.filter(user=user_id)
        if phone_number:
            queryset = queryset.filter(user__phone_number=phone_number)
        return queryset


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
    serializer_class = SendMoneyExternalSerializer
    permission_classes = [IsAuthenticated]


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


class TransactionStats(APIView):
    # serializer_class = TransactionStatsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        wallet = Wallet.objects.filter(user=user).first()
        if not wallet:
            self.permission_denied(self.request, message="Wallet not found")
        return wallet

    def get(self, request, tr_id, *args, **kwargs):
        wallet = get_object_or_404(Wallet.objects.all(), id=tr_id)
        today = timezone.now()

        months_back = [
            (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            for i in reversed(range(12))
        ]
        transactions = Transaction.objects.filter(
            created_at__gte=months_back[0],
        )

        months = []
        credits = (
            transactions.filter(to_wallet=wallet)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )
        debits = (
            transactions.filter(from_wallet=wallet)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        print(months_back)

        month_labels = [calendar.month_abbr[m.month] for m in months_back]

        # Map year-month strings for matching, e.g., '2024-06'
        month_keys = [m.strftime("%Y-%m") for m in months_back]

        # print(debits)

        # In credit_map = {entry["month"].strftime("%Y-%m"): entry["total"] for entry in credits}
        credit_map = {
            entry["month"].strftime("%Y-%m"): entry["total"] for entry in credits
        }
        debit_map = {
            entry["month"].strftime("%Y-%m"): entry["total"] for entry in debits
        }

        print(debit_map)

        credit_data = [credit_map.get(key, 0) for key in month_keys]
        debit_data = [debit_map.get(key, 0) for key in month_keys]

        return Response(
            {
                "months": month_labels,
                "data": {
                    "credits": credit_data,
                    # "data": credit_data,
                    "debits": debit_data,
                },
            }
        )
