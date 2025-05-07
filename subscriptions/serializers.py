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
    features = serializers.ListField(write_only=True)

    class Meta:
        exclude = []
        model = Subscription

    def validate(self, attrs):
        attrs = super().validate(attrs)

        features_str = attrs.get("features")

        print(features_str)

        features = []

        if features_str:
            for feature in features_str:
                _, created = SubscriptionFeature.objects.get_or_create(content=feature)

                features.append(_)

        attrs["features"] = features

        return attrs
