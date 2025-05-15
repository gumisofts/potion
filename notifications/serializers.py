from rest_framework.serializers import ModelSerializer

from notifications.models import *


class NotificationSerilizer(ModelSerializer):

    class Meta:
        exclude = []
        model = Notification
