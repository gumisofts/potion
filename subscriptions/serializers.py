from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from subscriptions.models import *


class UserSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = UserSubscription
        exclude = []

    def create(self, validated_data):
        manager = SubscriptionManager()

        return manager.subscribe(**validated_data)
