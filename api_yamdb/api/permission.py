from rest_framework import permissions


class UserAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'admin' or request.user.is_staff is True:
            return True
        return False
