from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from notifications.models import *
from notifications.serializers import *


class NotificationViewset(ListModelMixin, GenericViewSet):
    serializer_class = NotificationSerilizer
    queryset = Notification.objects.all()

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        if user:
            queryset = queryset.filter(Q(groups__in=user.objects.all()) | Q(user=user))

        return queryset
