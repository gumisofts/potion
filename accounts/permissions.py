from rest_framework.permissions import BasePermission


class BusinnessItemPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            self.has_permission(request, view)
            and request.user.businesses.filter(id=obj.business.id).exists()
        )


class UsersOwnProfilePermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user
