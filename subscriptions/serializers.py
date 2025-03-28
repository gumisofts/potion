from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from subscriptions.models import *

<<<<<<< HEAD
from accounts.models import *
from .models import *

=======
>>>>>>> dev-v01

class UserSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = UserSubscription
        exclude = []

    def create(self, validated_data):
        manager = SubscriptionManager()

        return manager.subscribe(**validated_data)


class SubscriptionSerializer(ModelSerializer):
    class Meta:
<<<<<<< HEAD
        model = Subscription
        fields = (
            "name",
            "frequency",
            "fixed_price",
            "has_fixed_price",
            "is_active"
        )
        read_only_fields = ("id", "service")

    
    def create(self, validated_data):
        """
        Handles Business service creation.
        """

        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User is not authenticated.")
        
        business = Business.objects.filter(owner=request.user).first()
        if not business:
            raise serializers.ValidationError("No business found for the authenticated user.")
        
        service = Service.objects.filter(business=business).first()

        if not service:
            raise serializers.ValidationError("No service found for the authenticated user.")

        subscription = Subscription.objects.create(
            service=request.user,
            name=validated_data.get("name"),
            frequency=validated_data.get("frequency"),
            fixed_price=validated_data.get("fixed_price"),
            has_fixed_price=validated_data.get("has_fixed_price", True),
            is_active=validated_data.get("is_active", True)
        )

        return subscription

    def update(self, instance, validated_data):
        """
        Handles Service subscription updates.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.frequency = validated_data.get("frequency", instance.frequency)
        instance.fixed_price = validated_data.get("fixed_price", instance.fixed_price)
        instance.has_fixed_price = validated_data.get("has_fixed_price", instance.has_fixed_price)
        instance.is_active = validated_data.get("is_active", instance.is_active)

        instance.save()
        return instance
=======
        exclude = []
        model = Subscription
>>>>>>> dev-v01
