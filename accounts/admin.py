from django.contrib import admin

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "phone_number",
        "first_name",
        "last_name",
        "is_phone_verified",
    ]


class TempraryCodeAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "code", "created_at"]


class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ["code_type", "user", "is_used", "expires_at"]


admin.site.register(User, UserAdmin)
admin.site.register(Business)
admin.site.register(Service)
admin.site.register(EmailConfirmationToken)
admin.site.register(TemporaryCode, TempraryCodeAdmin)
admin.site.register(VerificationCode, VerificationCodeAdmin)
