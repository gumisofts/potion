from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Enterprise
from .permissions import *
from .serializers import *


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=int,
                description="Filter by user ID",
                required=False,
            ),
            OpenApiParameter(
                name="status",
                type=str,
                description="Filter by grant status",
                required=False,
            ),
            OpenApiParameter(
                name="expires_at_gte",
                type=str,
                description="Filter by expiration date greater than or equal to",
                required=False,
            ),
        ]
    )
)
class EnterpriseUserGrantViewset(CreateModelMixin, ListModelMixin, GenericViewSet):
    """
    API endpoint that allows user grants to be viewed or edited.
    """

    queryset = UserGrant.objects.all()
    serializer_class = UserGrantSerializer
    permission_classes = [IsEnterprise]

    def get_queryset(self):
        """
        Optionally restricts the returned user grants to a given user,
        by filtering against a `user_id` query parameter in the URL.
        """
        queryset = self.queryset
        user_id = self.request.query_params.get("user_id", None)
        status = self.request.query_params.get("status", None)
        expires_at_gte = self.request.query_params.get("expires_at_gte", None)

        if expires_at_gte is not None:
            queryset = queryset.filter(expires_at__gte=expires_at_gte)

        if status is not None:
            queryset = queryset.filter(grant_status=status)
        queryset = queryset.filter(enterprise=self.request.user)

        if user_id is not None:
            queryset = queryset.filter(user=user_id)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="user_id", type=OpenApiTypes.UUID, required=False),
            OpenApiParameter(name="status", type=OpenApiTypes.STR, required=False),
            OpenApiParameter(
                name="expires_at_gte", type=OpenApiTypes.DATETIME, required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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


class UserGrantViewset(ListModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = UserGrant.objects.all()
    serializer_class = UserGrantSerializerForUser
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned user grants to a given user,
        by filtering against a `user_id` query parameter in the URL.
        """
        queryset = self.queryset
        status = self.request.query_params.get("status", None)
        expires_at_gte = self.request.query_params.get("expires_at_gte", None)

        if expires_at_gte is not None:
            queryset = queryset.filter(expires_at__gte=expires_at_gte)

        if status is not None:
            queryset = queryset.filter(grant_status=status)
        queryset = queryset.filter(user=self.request.user)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="user_id", type=OpenApiTypes.UUID, required=False),
            OpenApiParameter(name="status", type=OpenApiTypes.STR, required=False),
            OpenApiParameter(
                name="expires_at_gte", type=OpenApiTypes.DATETIME, required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AccessGrantViewset(CreateModelMixin, GenericViewSet):
    serializer_class = AccessGrantSerializer
    permission_classes = [IsEnterprise]
