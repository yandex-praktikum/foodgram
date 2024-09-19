"""backend/recipes/views.py

"""
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import AllowAny

from recipes.models import (
    Ingredient,
    Tag,
)
from recipes.serializers import (
    IngredientReadSerializer,
    TagReadSerializer,
)


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Ингредиенты

    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientReadSerializer
    pagination_class = None
    permission_classes = (AllowAny, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', )


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
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

    queryset = Tag.objects.all()
    serializer_class = TagReadSerializer
    pagination_class = None
    permission_classes = (AllowAny, )
