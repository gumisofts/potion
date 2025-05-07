from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet


class UtilityViewset(CreateModelMixin, GenericViewSet):
    serializer_class = None
    queryset = None
