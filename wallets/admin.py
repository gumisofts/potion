from django.contrib import admin

from .models import Transaction, Wallet


class WalletAdmin(admin.ModelAdmin):
    list_display = ["id", "balance", "user__id"]


admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction)
