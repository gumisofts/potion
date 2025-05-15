from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "content", "delivery_method"]


admin.site.register(Notification, NotificationAdmin)
