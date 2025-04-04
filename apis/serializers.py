from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from apis.models import *


def default_key_generator():
    return


class ApiKeySerializer(ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    hashed_key = serializers.HiddenField(default=default_key_generator)
    key = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = ApiKey
        exclude = []
        read_only_fiels = ["id", "hashed_key"]
