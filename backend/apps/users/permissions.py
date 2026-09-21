from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """仅管理员"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrReception(BasePermission):
    """管理员或前台"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'reception']

