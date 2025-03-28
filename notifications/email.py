from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_html_email(subject: str, html_message: str, recipients: list):
    html_message = render_to_string(
        "email.html", {"subject": subject, "message": html_message}
    )

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.EMAIL_USER,
        to=recipients,
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)
