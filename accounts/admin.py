from django.contrib import admin

from .models import Business, EmailConfirmationToken, Service, User

admin.site.register(User)
admin.site.register(Business)
admin.site.register(Service)
admin.site.register(EmailConfirmationToken)
