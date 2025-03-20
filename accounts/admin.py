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
    list_display = ["phone_number", "code", "user_id", "created_at"]

    def user_id(self, instance):
        user = User.objects.filter(phone_number=instance.phone_number).first()

        if user:
            return user.id


class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ["code_type", "user", "is_used", "expires_at"]


admin.site.register(User, UserAdmin)
admin.site.register(Business)
admin.site.register(Service)
admin.site.register(EmailConfirmationToken)
admin.site.register(TemporaryCode, TempraryCodeAdmin)
admin.site.register(VerificationCode, VerificationCodeAdmin)
