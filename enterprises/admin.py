from django.contrib import admin

from .models import *


class EnterpriseAdmin(admin.ModelAdmin):
    list_display = (
        "long_name",
        "short_name",
        "description",
        "logo",
        "is_active",
        "pull_limit",
    )
    search_fields = ("long_name", "short_name")
    list_filter = ("is_active",)
    ordering = ("created_at",)
    list_per_page = 20


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("key",)


class UserGrantAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "enterprise",
        "max_amount",
        "expires_at",
        "created_at",
    )
    search_fields = ("user__username", "enterprise__long_name")
    list_filter = ("expires_at",)
    ordering = ("created_at",)
    list_per_page = 100


class AccessGrantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client_id",
        "scope",
        "is_active",
        "actions_call_back",
    )
    search_fields = ("key", "enterprise__long_name")
    ordering = ("created_at",)
    list_per_page = 100
    search_fields = ("key", "enterprise__long_name")


admin.site.register(Enterprise, EnterpriseAdmin)
admin.site.register(AccessGrant, AccessGrantAdmin)
admin.site.register(UserGrant, UserGrantAdmin)
