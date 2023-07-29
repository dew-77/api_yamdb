from rest_framework.permissions import SAFE_METHODS, BasePermission


class OnlyAdmin(BasePermission):
    """Право доступа только для пользователей c ролью 'admin'."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.role == "admin"
        return False


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            if (request.user.role == "admin"
                or request.user.role == "moderator"
                    or request.user.is_superuser):
                return True

            if obj.author == request.user:
                return True

        return False
