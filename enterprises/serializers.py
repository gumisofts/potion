from rest_framework.serializers import ModelSerializer

from rest_framework import serializers
from .models import *


class EnterpriseSerializer(ModelSerializer):
    class Meta:
        exclude = []
        model = Enterprise
