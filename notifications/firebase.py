import firebase_admin
from django.conf import settings
from firebase_admin import credentials, messaging

# Path to your service account key file

# Device token you want to send the notification to


cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred)


def send_push_notification(fcm_token, title, body, data=None):
    """
    Send a notification using Firebase Cloud Messaging (FCM).

    :param title: The title of the notification.
    :param body: The body of the notification.
    :param data: Optional custom data to include with the notification.
    """

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=fcm_token,
            data=data or {},
        )
        response = messaging.send(message)
        # Check if the token is valid
    except Exception as e:
        print(e)
        return False

    # Send the message
    return True
