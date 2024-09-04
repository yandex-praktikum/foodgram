from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение, дающее доступ только администратору или суперпользователю"""
    def has_permission(self, request, view):
        if (
            request.user and request.user.is_authenticated
            and request.user.is_admin
        ):
            return True

    def has_object_permission(self, request, view, obj):
        if (
            (request.user and request.user.is_authenticated)
            and (request.user.is_admin or request.user.is_superuser)
        ):
            return True
        return super().has_object_permission(request, view, obj)


class IsAuthenticated(permissions.BasePermission):
    """Разрешение, дающее доступ только аутентифицированному юзеру"""
    def has_permission(self, request, view):
        if (request.user and request.user.is_authenticated):
            return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, дающее доступ к редактированию только
    автору контента или админу
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )