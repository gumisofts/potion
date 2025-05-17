from django.contrib import admin

from .models import Subscription, UserSubscription


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


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
