from django.dispatch import Signal

user_registered = Signal()
user_registered_successfully = Signal()
user_logged_in = Signal()
send_verification_code = Signal()
user_phone_confirmed = Signal()
user_email_confirmed = Signal()
