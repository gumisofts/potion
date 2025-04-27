from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import *


class EnterpriseSerializer(ModelSerializer):
    class Meta:
        exclude = []
        model = Enterprise
