from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        is_authenticated = user.is_authenticated
        user_role = user.role == 'admin'
        if is_authenticated and user and user_role:
            return True
        return False


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        is_authenticated = user.is_authenticated
        user_role = user.role == 'owner'
        if is_authenticated and user and user_role:
            return True
        return False


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        is_authenticated = user.is_authenticated
        user_role = user.role == 'staff'
        if is_authenticated and user and user_role:
            return True
        return False


class IsHigherStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        is_authenticated = user.is_authenticated
        user_role = user.role == 'higher-staff'
        if is_authenticated and user and user_role:
            return True
        return False
