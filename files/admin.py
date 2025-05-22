from django.contrib import admin

from files.models import FileMeta

# Register your models here.


class FileMetaAdmin(admin.ModelAdmin):
    list_display = ("key", "public_url", "created_at", "updated_at")


admin.site.register(FileMeta, FileMetaAdmin)
