"""backend/recipes/serializers.py

"""
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Tag,
)


class IngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения списка ингредиентов.

    [GET]
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения тегов .

    Cписок тегов:
        - Запрос:
            GET /api/tags/
        - Ответы:
            200

    Получение тега
            GET /api/tags/{id}/
            PATH PARAMETERS:
                - id (required, string, Уникальный идентификатор Тега).
        - Ответы:
            - 200
            - 404 Объект не найден
    """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )
