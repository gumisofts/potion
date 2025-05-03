from datetime import datetime

from django.shortcuts import get_object_or_404, render
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import Q

from accounts.permissions import *

from .models import *
from subscriptions.models import *
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
                from_wallet__user=user,
                status='completed'
            )
            spend_data = transactions.aggregate(
                total=Sum('amount')
            )
            
            subscriptions = UserSubscription.objects.filter(
                user=user,
                is_active=True
            )
            sub_data = subscriptions.aggregate(
                total=Sum('subscription__fixed_price')
            )
            
            data.append({
                'user_id': user.id,
                'phone_number': user.phone_number,
                'is_phone_verified': user.is_phone_verified,
                'total_spend': spend_data.get('total') or 0,
                'subscription_sum': sub_data.get('total') or 0,
                'is_active_subscriber': subscriptions.exists()
            })
        
        return Response(data)
    


class TransactionRecordViewset(GenericViewSet, ListModelMixin):
    serializer_class = TransactionRecordSerializer
    queryset = Transaction.objects.all()
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=start_date)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(created_at__lte=end_date)
        
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(
                Q(from_wallet__user__id=user_id) | 
                Q(to_wallet__user__id=user_id)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)