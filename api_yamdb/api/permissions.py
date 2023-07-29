from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnly(BasePermission):
    """Право доступа для анонимных пользователей."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAdmin(BasePermission):
    """Право доступа только для администраторов и выше."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_authenticated and (
                request.user.role == "admin" or request.user.is_superuser))


class IsAuthorOrReadOnly(BasePermission):
    """Право доступа для авторов объектов."""
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_authenticated and obj.author == request.user:
            return True

        return request.user.is_superuser


class IsModeratorOrAdminOrReadOnly(BasePermission):
    """Право доступа для модераторов и выше."""
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                request.user.role == "moderator"
                or request.user.role == "admin"
                or request.user.is_superuser)
        )
