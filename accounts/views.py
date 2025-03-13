from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import User, EmailConfirmationToken
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer
from .utils import send_confirmation_email


class Home(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            user: User = request.user
            custom_data = {
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "message": "Hello, World!",
            }
            return Response(custom_data)
        except Exception as e:
            return Response({"error": str(e)}, status=401)


class Logout(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            user: User = serializer.create(validated_data=serializer.validated_data)
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            access = refresh.access_token

            access_token_payload = AccessToken(str(access)).payload

            return Response(
                {
                    "user": serializer.data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "access_token_payload": access_token_payload,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInformationAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            user: User = request.user
            payload = {
                "email": user.email,
                "is_email_confirmed": user.is_email_confirmed,
            }
            return Response(data=payload, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=401)


class SendEmailConfirmationTokenAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        try:
            user: User = request.user
            token = EmailConfirmationToken.objects.create(user=user)
            send_confirmation_email(
                email=user.email, token_id=token.pk, user_id=user.pk
            )
            return Response(data=None, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=401)


def confirm_email_view(request):
    token_id = request.GET.get("token_id", None)
    user_id = request.GET.get("user_id", None)
    try:
        token = EmailConfirmationToken.objects.get(pk=token_id)
        user = token.user
        user.is_email_confirmed = True
        user.save()
        data = {"is_email_confirmed": True}
        return render(
            request, template_name="accounts/confirm_email_view.html", context=data
        )
    except EmailConfirmationToken.DoesNotExist:
        data = {"is_email_confirmed": False}
        return render(
            request, template_name="accounts/confirm_email_view.html", context=data
        )
