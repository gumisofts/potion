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

    def get_queryset(self):
        queryset = super().get_queryset()

        phone_number = self.request.query_params.get("phone_number")

        if phone_number:
            queryset = queryset.filter(phone_number=phone_number)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="phone_number", required=False, type=OpenApiTypes.STR)
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserProfileViewset(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):

    serializer_class = UserProfileSerializer
    permission_classes = [UsersOwnProfilePermission]
    queryset = User.objects.filter(is_active=True)

    def get_object(self):
        return self.request.user

    @extend_schema(
        description="Retrieve or update the authenticated user's profile",
        responses={
            200: UserProfileSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


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
    queryset = Service.objects.all()
    permission_classes = [BusinnessItemPermission]

    def get_queryset(self):
        queryset = self.queryset

        business_id = self.request.GET.get("business_id")
        categories = self.request.GET.get("categories")

        is_active = self.request.GET.get("is_active")
        if is_active:
            queryset = queryset.filter(is_active=is_active)

        if categories:
            categories = categories.split(",")
            queryset = queryset.filter(categories__in=categories)

        if business_id:
            queryset = queryset.filter(business=business_id)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="business_id",
                type=OpenApiTypes.UUID,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.STR,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="categories",
                type=OpenApiTypes.STR,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
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


class CategoriesViewset(ListModelMixin, GenericViewSet):
    serializer_class = CategoriesSerializer
    queryset = Category.objects.all()


class RequestPasswordResetViewset(CreateModelMixin, GenericViewSet):
    serializer_class = RequestPasswordResetSerializer
    permission_classes = []

    @extend_schema(
        description="Request a password reset code to be sent to the user's phone number",
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ConfirmPasswordResetViewset(CreateModelMixin, GenericViewSet):
    serializer_class = ConfirmPasswordResetSerializer
    permission_classes = []

    @extend_schema(
        description="Confirm password reset using the code sent to the user's phone",
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# Write A view To reset
