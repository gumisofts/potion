from rest_framework.permissions import BasePermission


class IsEnterprise(BasePermission):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)

    def has_permission(self, request, view):
        return super().has_permission(request, view)
