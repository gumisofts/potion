from django.contrib import admin

from bills.models import *


class UtilityAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


class BillingAdmin(admin.ModelAdmin):
    list_display = ["id", "amount"]


class UtilityUserAdmin(admin.ModelAdmin):
    list_display = ["id", "number", "phone_number"]


admin.site.register(Utility, UtilityAdmin)
admin.site.register(Billing, BillingAdmin)
admin.site.register(UtilityUser, UtilityUserAdmin)
