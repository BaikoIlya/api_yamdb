from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class UserAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'admin' or request.user.is_staff is True:
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_admin
            )
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ReviewAndCommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and (
                obj.author == request.user or request.user.role == 'moderator')
        )
