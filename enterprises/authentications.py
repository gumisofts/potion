from django.contrib.auth.hashers import check_password, make_password
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import *


class EnterpriseAPIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_id = request.headers.get("X-Access-ID")
        access_secret = request.headers.get("X-Access-Secret")

        if not access_id or not access_secret:
            return None

        try:
            grant = AccessGrant.objects.get(access_id=access_id)
        except Enterprise.DoesNotExist:
            raise AuthenticationFailed("Invalid Access ID")

        if not check_password(access_secret, grant.access_secret):
            raise AuthenticationFailed("Invalid Access Secret")

        grant.enterprise.is_authenticated = True
        grant.enterprise.is_enterprise = True

        return (grant.enterprise, None)
