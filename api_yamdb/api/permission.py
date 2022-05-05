from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class UserAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated and (
                    request.user.role == 'admin' or request.user.is_superuser
                )
            )
        )


class ReviewAndCommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and (
                obj.author == request.user or request.user.role == 'moderator')
        )
