from rest_framework import permissions


class IsAdminIsAuthorOrReadOnly(permissions.BasePermission):
    """
    Неавторизованным пользователям – только просмотр.
    Администраторам и владельцам записи доступны остальные методы.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_superuser
                or request.user.is_admin
                or obj.author == request.user)


class IsAdminIsAuthor(permissions.BasePermission):
    """
    Доступ к объекту только по безопасным запросам, либо
    superuser Django, аутентифицированным пользователям с ролью admin,
    а также автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_admin
                 or obj.author == request.user)
        )
