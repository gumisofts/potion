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
        # Check if the user is an external system
        return hasattr(request.user, "is_external") and request.user.is_external

    def has_object_permission(self, request, view, obj):
        # Check if the user is an external system
        return hasattr(request.user, "is_external") and request.user.is_external
