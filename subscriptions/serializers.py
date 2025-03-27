from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from subscriptions.models import *


class UserSubscriptionSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserSubscription
        exclude = []

    def create(self, validated_data):
        manager = SubscriptionManager()

        return manager.subscribe(**validated_data)


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        exclude = []
        model = Subscription
