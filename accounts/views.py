from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from .models import *
from .serializers import *
from .utils import send_confirmation_email
from datetime import datetime
from django.shortcuts import get_object_or_404


class Logout(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class RegisterViewset(GenericViewSet, CreateModelMixin):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class UsersViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = UserGeneralInfoSerializer

    queryset = User.objects.filter(is_active=True)


class VerificationCodeViewset(CreateModelMixin, GenericViewSet):
    serializer_class = CreateVerificationCodeSerializer
    # queryset = VerificationCode.objects.all()
