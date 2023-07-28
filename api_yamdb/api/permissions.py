from rest_framework.permissions import BasePermission


class OnlyAdmin(BasePermission):
    """Право доступа только для пользователей c ролью 'admin'."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_superuser or request.user.role == 'admin')
        return False
