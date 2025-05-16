from django.contrib import admin

from sandbox.models import *


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ["account_number", "first_name", "last_name", "institution__name"]


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "id"]


class InstitutionWalletAdmin(admin.ModelAdmin):
    list_display = ["id", "balance"]


class InstitutionTransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "amount", "first_name", "last_name"]


admin.site.register(InstitutionWallet, InstitutionWalletAdmin)
admin.site.register(InstitutionTransaction, InstitutionTransactionAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
