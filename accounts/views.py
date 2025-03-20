from datetime import datetime

from django.shortcuts import get_object_or_404, render
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

from .models import *
from .serializers import *
from .utils import send_confirmation_email


class Logout(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class LoginViewset(GenericViewSet, CreateModelMixin):
    serializer_class = UserLoginSerializer


class RegisterViewset(GenericViewSet, CreateModelMixin):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class UsersViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = UserGeneralInfoSerializer
    permission_classes = [IsAuthenticated]

    queryset = User.objects.filter(is_active=True)


class VerificationCodeViewset(CreateModelMixin, GenericViewSet):
    serializer_class = CreateVerificationCodeSerializer


class VerificationCodeResendViewset(CreateModelMixin, GenericViewSet):
    serializer_class = ResendVerificationSerializer
