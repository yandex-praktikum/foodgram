"""backend/recipes/views.py

"""
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import AllowAny

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
)
from recipes.serializers import (
    IngredientReadSerializer,
    TagReadSerializer,
    RecipeReadSerializer
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
    queryset = Tag.objects.all()
    serializer_class = TagReadSerializer
    pagination_class = None
    permission_classes = (AllowAny, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    #pagination_class = CustomPaginator
    #permission_classes = (IsAuthorOrReadOnly, )
    #filter_backends = (DjangoFilterBackend, )
    #filterset_class = RecipeFilter
    #http_method_names = ['get', 'post', 'patch', 'create', 'delete']

