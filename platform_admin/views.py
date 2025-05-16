from datetime import datetime

from django.db import transaction as db_transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from accounts.permissions import *
from subscriptions.models import *

from .models import *
from .serializers import *


class LoginViewset(GenericViewSet, CreateModelMixin):
    serializer_class = AdminLoginSerializer


class UsersDataViewset(GenericViewSet, ListModelMixin):
    serializer_class = UsersDataSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        data = []
        for user in User.objects.all():
            transactions = Transaction.objects.filter(
                from_wallet__user=user, status="completed"
            )
            spend_data = transactions.aggregate(total=Sum("amount"))

            subscriptions = UserSubscription.objects.filter(user=user, is_active=True)
            sub_data = subscriptions.aggregate(total=Sum("subscription__fixed_price"))

            data.append(
                {
                    "user_id": user.id,
                    "phone_number": user.phone_number,
                    "is_phone_verified": user.is_phone_verified,
                    "total_spend": spend_data.get("total") or 0,
                    "subscription_sum": sub_data.get("total") or 0,
                    "is_active_subscriber": subscriptions.exists(),
                }
            )

        return Response(data)


class TransactionRecordViewset(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = TransactionRecordSerializer
    queryset = Transaction.objects.all()
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            queryset = queryset.filter(created_at__lte=end_date)

        user_id = request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(
                Q(from_wallet__user__id=user_id) | Q(to_wallet__user__id=user_id)
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DisputeTransactionViewset(
    GenericViewSet, CreateModelMixin, ListModelMixin, RetrieveModelMixin
):
    serializer_class = DisputeTransactionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Dispute.objects.all()

    def get_permissions(self):
        if self.action in ["move_to_review", "mark_as_reviewed", "process_refund"]:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "move_to_review":
            return DisputeStatusUpdateSerializer
        elif self.action == "mark_as_reviewed":
            return DisputeReviewSerializer
        elif self.action == "process_refund":
            return DisputeRefundSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(transaction__from_wallet__user=self.request.user)
                | Q(transaction__to_wallet__user=self.request.user)
            )

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")

    @action(detail=True, methods=["patch"], url_path="move-to-review")
    def move_to_review(self, request, pk=None):
        dispute = self.get_object()
        serializer = self.get_serializer(
            dispute, data={"status": "in_review"}, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="mark-as-reviewed")
    def mark_as_reviewed(self, request, pk=None):
        dispute = self.get_object()
        serializer = self.get_serializer(
            dispute,
            data={"status": "reviewed", "notes": request.data.get("notes", "")},
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="process-refund")
    def process_refund(self, request, pk=None):
        dispute = self.get_object()

        with db_transaction.atomic():
            # Create refund transaction
            refund_tx = Transaction.objects.create(
                from_wallet=dispute.transaction.to_wallet,  # Original receiver
                to_wallet=dispute.transaction.from_wallet,  # Original sender
                amount=dispute.transaction.amount,
                status="completed",
                remarks=f"Refund for disputed transaction {dispute.transaction.id}",
            )

            # Update dispute status and link refund transaction
            serializer = self.get_serializer(
                dispute,
                data={"status": "resolved", "notes": "Refund processed"},
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            dispute = serializer.save()

            # Link the refund transaction
            dispute.refund_transaction = refund_tx
            dispute.save()

            # Update wallet balances (pseudo-code - adjust to your wallet logic)
            self._update_wallet_balances(refund_tx)

        return Response(serializer.data)

    def _update_wallet_balances(self, transaction):
        """Helper method to update wallet balances"""
        try:
            # Deduct from sender
            transaction.from_wallet.balance -= transaction.amount
            transaction.from_wallet.save()

            # Add to receiver
            transaction.to_wallet.balance += transaction.amount
            transaction.to_wallet.save()
        except Exception as e:
            raise ValidationError(f"Failed to update wallet balances: {str(e)}")


class BusinessRecordViewset(GenericViewSet, ListModelMixin):
    serializer_class = BusinessRecordSerializer
    queryset = Business.objects.all()
    permission_classes = [IsAdminUser]
