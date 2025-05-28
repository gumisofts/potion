from rest_framework.permissions import BasePermission


class IsWalletOwner(BasePermission):
    """
    Custom permission to only allow owners of a wallet to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the wallet
        return obj.user == request.user

    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user.is_authenticated


class ExternalSysPermission(BasePermission):
    """
    Custom permission to only allow external systems to access the view.
    """

    def has_permission(self, request, view):
        # Check for required headers
        access_id = request.META.get("HTTP_X_ACCESS_ID")
        access_secret = request.META.get("HTTP_X_ACCESS_SECRET")

        if not access_id or not access_secret:
            return False

        # TODO: Add proper access key validation here
        # For now, just check if headers are present
        return True

    def has_object_permission(self, request, view, obj):
        # Check for required headers
        access_id = request.META.get("HTTP_X_ACCESS_ID")
        access_secret = request.META.get("HTTP_X_ACCESS_SECRET")

        if not access_id or not access_secret:
            return False

        # TODO: Add proper access key validation here
        # For now, just check if headers are present
        return True
