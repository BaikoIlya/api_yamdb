from rest_framework import permissions


class UserAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'admin' or request.user.is_staff is True:
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            # or (
            #     request.user.is_authenticated
            #     and request.user.is_admin
            # )
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class UserAdminOnly_2(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.role == 'admin'
            or request.user.is_superuser
        )
