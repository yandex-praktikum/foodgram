from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientSearchFilter, RecipeFilter
from api.permissions import IsAdminIsAuthorOrReadOnly
from api.services import shopping_cart
from food.models import (Favorite, Ingredient, Recipe, ShoppingCart, Subscribe,
                         Tag, User)

from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateDeleteSerilizer,
                          RecipeListSerializer, ShoppingCartSerializer,
                          ShortLinkSerializer,
                          SubscribeListCreateDeleteSerializer, TagSerializer)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для модели тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminIsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ['get_short_link']:
            return ShortLinkSerializer
        if self.action in ['favorite']:
            return FavoriteSerializer
        if self.action in ['shopping_cart']:
            return ShoppingCartSerializer
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateUpdateDeleteSerilizer

    @action(detail=True,
            methods=('POST', 'DELETE'),
            permission_classes=[IsAuthenticated],
            )
    def favorite(self, request, *args, **kwargs):
        """
        Получить / Добавить / Удалить  рецепт
        из избранного у текущего пользоватля.
        """
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            if Favorite.objects.filter(
                author=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer_class()(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # method DELETE:
        if not Favorite.objects.filter(
            author=user, recipe=recipe
        ).exists():
            return Response(
                {'detail': 'Страница не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        Favorite.objects.get(recipe=recipe).delete()
        return Response(
            'Рецепт успешно удалён из избранного.',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated],
            )
    def shopping_cart(self, request, **kwargs):
        """
        Получить / Добавить / Удалить  рецепт
        из списка покупок у текущего пользоватля.
        """
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                author=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer_class()(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # method DELETE
        if not ShoppingCart.objects.filter(
            author=user, recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Страница не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.get(recipe=recipe).delete()
        return Response(
            'Рецепт успешно удалён из списка покупок.',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated],
            )
    def download_shopping_cart(self, request):
        """
        Скачать список покупок для выбранных рецептов,
        данные суммируются.
        """
        author = User.objects.get(id=self.request.user.pk)
        if author.shopping_cart.exists():
            return shopping_cart(self, request, author)
        return Response(
            'Список покупок пуст.',
            status=status.HTTP_404_NOT_FOUND
        )


class SubscribeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """Вьюсет для модели подписок."""
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeListCreateDeleteSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination


class ShortLinkAPIView(APIView):
    """Вьюсет для модели коротких ссылок."""
    permission_classes = []

    def get(self, request, **kwargs):
        request.data['long_url'] = ('/'.join(
            request.build_absolute_uri().split('/')[:-2]
        ) + '/')
        serializer = ShortLinkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token, status_code = serializer.create(
                validated_data=serializer.validated_data
            )
            return Response(
                ShortLinkSerializer(token).data, status=status_code)
        return Response(
            serializer.errors, status=status.HTTP_404_NOT_FOUND)
