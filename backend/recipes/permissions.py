"""Разрешения.

backend/recipes/permissions.py
"""

from rest_framework import permissions


class IsAuthorOrAdmin(permissions.IsAuthenticatedOrReadOnly):
    message = 'Запрос недоступен из-за ограничения прав.'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
