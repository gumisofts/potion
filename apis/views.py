from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apis.serializers import *


# Create your views here.
class ApiKeyViewset(ModelViewSet):
    serializer_class = ApiKeySerializer
    queryset = ApiKey.objects.filter()
