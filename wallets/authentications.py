from django.contrib.auth.hashers import check_password
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from wallets.models import AccessKey


class ExternalSysAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_id = request.headers.get("X-Access-Id")
        access_secret = request.headers.get("X-Access-Secret")
        if not access_id or not access_secret:
            return None

        try:
            grant = AccessKey.objects.get(access_id=access_id)
            print(f"Grant found: {grant.access_id}")
        except AccessKey.DoesNotExist:
            print(f"Grant not found for access_id: {access_id}")
            return

        if not check_password(access_secret, grant.access_secret):
            return

        grant.is_authenticated = True
        grant.is_external = True

        print(f"Authenticated external system: {grant.access_id}")

        return (grant, None)
