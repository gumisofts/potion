from django.contrib import admin

from .models import *


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "service",
        "frequency",
        "fixed_price",
        "has_fixed_price",
        "is_active",
    ]


class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "subscription", "is_active", "next_billing_date"]


class SubscriptionFeatureAdmin(admin.ModelAdmin):
    list_display = ["id", "content"]


admin.site.register(SubscriptionFeature, SubscriptionFeatureAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
