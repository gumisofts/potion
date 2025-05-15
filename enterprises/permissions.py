from rest_framework.permissions import BasePermission


class IsEnterprise(BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(request.user, "is_enterprise") and request.user.is_enterprise

    def has_permission(self, request, view):
        return hasattr(request.user, "is_enterprise") and request.user.is_enterprise
