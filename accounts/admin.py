from django.contrib import admin

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "phone_number",
        "first_name",
        "last_name",
        "is_phone_verified",
    ]


class TempraryCodeAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "code", "user_id", "created_at"]

    def user_id(self, instance):
        user = User.objects.filter(phone_number=instance.phone_number).first()

        if user:
            return user.id


class BusinnesAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "contact_phone",
        "contact_email",
        "is_active",
        "is_verified",
    ]
    list_filter = ["is_verified"]


class ServiceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "business"]
    list_filter = ["business__id"]


class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ["code_type", "user", "is_used", "expires_at"]


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ["label", "id"]


admin.site.register(User, UserAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(EmailConfirmationToken)
admin.site.register(TemporaryCode, TempraryCodeAdmin)
admin.site.register(VerificationCode, VerificationCodeAdmin)
