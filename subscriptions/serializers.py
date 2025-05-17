from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from subscriptions.models import *


class UserSubscriptionSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_active = serializers.BooleanField(read_only=True)
    subscription = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.filter(is_active=True)
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        subscription = attrs.get("subscription")
        user = attrs.get("user")

        if (
            subscription.payment_type == "pre"
            and subscription.fixed_price > user.wallet.balance
        ):
            raise serializers.ValidationError(
                {"detail": "Not enough balance in wallet for this subscription"}
            )
        return attrs

    def create(self, validated_data):

        return UserSubscription.objects.subscribe(**validated_data)


class UnsubscribeSerializer(UserSubscriptionSerializer):
    def create(self, validated_data):
        return UserSubscription.objects.unsubscribe(**validated_data)


class FeaturesSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionFeature
        exclude = []


class SubscriptionSerializer(ModelSerializer):
    features = FeaturesSerializer(many=True)

    class Meta:
        exclude = []
        model = Subscription

    def create(self, validated_data):
        features = []
        for feature in validated_data.pop("features", []):
            _, created = SubscriptionFeature.objects.get_or_create(**feature)
            features.append(_)

        subs = super().create(validated_data)

        subs.features.set(features)

        return subs
