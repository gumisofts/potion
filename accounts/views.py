from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import User
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer


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
