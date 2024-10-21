from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение, которое позволяет редактировать только авторам,
    а всем остальным - только просмотр.
    """

    def has_permission(self, request, view):
        # Разрешить доступ к GET-запросам всем пользователям
        if request.method in SAFE_METHODS:
            return True
        # Для других методов требуется аутентификация
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Разрешить доступ к объекту (рецепту) только автору
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
