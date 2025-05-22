from django.contrib import admin

from .models import *


class WalletAdmin(admin.ModelAdmin):
    list_display = ["id", "user__phone_number", "balance", "wallet_type", "user__id"]
    list_filter = ["user"]


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "status", "remarks", "created_at", "updated_at")
    ordering = ("-created_at",)
    list_filter = ("status",)
    search_fields = (
        "remarks",
        "from_wallet__user__phone_number",
        "to_wallet__user__phone_number",
    )


class AccessKeyAdmin(admin.ModelAdmin):
    list_display = ("access_id", "created_at", "updated_at")
    ordering = ("-created_at",)
    search_fields = ("key",)
    list_filter = ("created_at",)


admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(AccessKey, AccessKeyAdmin)
