from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext

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


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active"]


@admin.action(description="Verify selected businesses")
def verify_business(self, request, queryset):
    for business in queryset:
        business.is_verified = True
        business.save()
    self.message_user(request, "Selected businesses have been verified.")


class BusinessAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "contact_phone",
        "contact_email",
        "is_active",
        "is_verified",
        "owner",
        "logo_url",
        "license_url",
    ]

    def logo_url(self, instance):

        if instance.logo:
            url = instance.logo.public_url
            return mark_safe(gettext(f'<a href="{url}">{instance.logo.id}</a>'))

    def license_url(self, instance):

        if instance.license:
            url = instance.license.public_url
            return mark_safe(gettext(f'<a href="{url}">{instance.license.id}</a>'))

    list_filter = ["is_verified"]
    actions = [verify_business]


admin.site.register(User, UserAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)
admin.site.register(Business, BusinessAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(TemporaryCode, TempraryCodeAdmin)
admin.site.register(VerificationCode, VerificationCodeAdmin)
admin.site.register(Category, CategoryAdmin)
