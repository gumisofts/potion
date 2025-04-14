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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from accounts.permissions import *

from .models import *
from .serializers import *
from .utils import send_confirmation_email


class LoginViewset(GenericViewSet, CreateModelMixin):
    serializer_class = UserLoginSerializer


class RegisterViewset(GenericViewSet, CreateModelMixin):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = []


class UsersViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = UserGeneralInfoSerializer
    permission_classes = [IsAuthenticated]

    queryset = User.objects.filter(is_active=True)


class VerificationCodeViewset(CreateModelMixin, GenericViewSet):
    serializer_class = CreateVerificationCodeSerializer


class VerificationCodeResendViewset(CreateModelMixin, GenericViewSet):
    serializer_class = ResendVerificationSerializer


class BusinessViewset(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    serializer_class = BusinessSerializer
    queryset = Business.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.GET.get("user_id")

        queryset = self.queryset

        if user_id:
            queryset = queryset.filter(owner=user_id)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.UUID,
                required=False,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BusinessServiceViewset(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    serializer_class = BusinessServiceSerializer
    queryset = Service.objects.filter(is_active=True)
    permission_classes = [BusinnessItemPermission]

    def get_queryset(self):
        queryset = self.queryset

        business_id = self.request.GET.get("business_id")

        if business_id:
            queryset = queryset.filter(business=business_id)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="bussines_id",
                type=OpenApiTypes.UUID,
                required=False,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserDeviceViewset(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    serializer_class = UserDeviceSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserDevice.objects.filter()
