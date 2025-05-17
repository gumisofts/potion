from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsEnterprise(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            hasattr(request.user, "is_enterprise")
            and request.user.is_enterprise
            or request.method in SAFE_METHODS
        )

    def has_permission(self, request, view):
        return hasattr(request.user, "is_enterprise") and request.user.is_enterprise


class IsEnterpriseOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(request.user)
        return (
            hasattr(request.user, "is_enterprise")
            and request.user.is_enterprise
            or request.method in SAFE_METHODS
        )

    def has_permission(self, request, view):
        print(request.user)
        return (
            hasattr(request.user, "is_enterprise")
            and request.user.is_enterprise
            or request.method in SAFE_METHODS
        )
