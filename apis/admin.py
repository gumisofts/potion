from datetime import datetime

from django.contrib import admin

from apis.models import *


class KeyAdmin(admin.ModelAdmin):
    list_display = ["business", "hashed_key", "expired", "created_at", "updated_at"]
    list_filter = []

    def expired(self, instance: ApiKey):

        return instance.expires_at > datetime.now()


admin.site.register(ApiKey, KeyAdmin)
