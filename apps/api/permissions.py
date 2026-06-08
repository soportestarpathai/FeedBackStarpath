from rest_framework.permissions import BasePermission
from apps.accounts.models import CustomUser


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == CustomUser.SUPERADMIN


class IsAdminOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in (
            CustomUser.ADMIN, CustomUser.SUPERADMIN
        )


class IsTesterOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in (
            CustomUser.TESTER, CustomUser.ADMIN, CustomUser.SUPERADMIN
        )
