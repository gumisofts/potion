from django.contrib import admin

from .models import Transaction, Wallet


class WalletAdmin(admin.ModelAdmin):
    list_display = ["id", "user__phone_number", "balance", "wallet_type", "user__id"]
    list_filter = ["user"]


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "status", "remarks")


admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction, TransactionAdmin)
