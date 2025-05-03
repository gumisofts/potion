from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from subscriptions.models import *


class UserSubscriptionSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_active = serializers.BooleanField(read_only=True)
    subscription = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.filter(is_active=True)
    )

    def create(self, validated_data):

        return UserSubscription.objects.subscribe(**validated_data)


class UnsubscribeSerializer(UserSubscriptionSerializer):
    def create(self, validated_data):
        return UserSubscription.objects.unsubscribe(**validated_data)


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        exclude = []
        model = Subscription


class UserSubscriptionSerializer(ModelSerializer):
    class Meta:
        exclude = []
        model = UserSubscription
