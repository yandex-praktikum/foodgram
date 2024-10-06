"""backend/recipes/views.py

"""

from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.filters import (
    IngredientFilter,
    RecipeFilter,
)
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Subscriber,
    Tag,
    UserFavoriteRecipe,
    UserShoppingCartRecipe,
)
from recipes.paginations import LimitPagination
from recipes.permissions import IsAuthorOrAdmin
from recipes.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeCUDSerializer,
    ShortLinkSerializer,
    SubscriberSerializer,
    TagSerializer,
    UserSerializer,
    UserAvatarSerializer,
    UserFavoriteRecipesSerializer,
    UserShoppingCartRecipesSerializer,
)
from recipes.utils import get_shopping_cart_file

User = get_user_model()


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny, )
    filter_backends = (
        DjangoFilterBackend, SearchFilter,
    )
    filterset_class = IngredientFilter
    search_fields = ('^name', )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny, )
    filter_backends = (SearchFilter,)
    search_fields = ('^name', )


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPagination
    permission_classes = (IsAuthorOrAdmin, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action == 'favorite':
            return UserFavoriteRecipesSerializer
        elif self.action == 'shopping_cart':
            return UserShoppingCartRecipesSerializer
        return RecipeCUDSerializer

    def add_in_list(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = self.get_serializer(
            data={
                'user': self.request.user,
                'recipe': recipe.id
            }
        )
        serializer.is_valid(raise_exception=True)
        # Замечание: Валидацию выносим в сериализатор.
        model = serializer.Meta.model
        if not model.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            serializer.save(
                recipe=recipe
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': 'Рецепт уже в списке.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def delete_from_list(request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        existing_recipe, _ = model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()

        if not existing_recipe:
            return Response(
                {'Такой рецепт отсутствует.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.add_in_list(
            request,
            pk,
        )

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk):
        return self.delete_from_list(
            request,
            pk,
            UserFavoriteRecipe,
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.add_in_list(request, pk)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        return self.delete_from_list(
            request,
            pk,
            UserShoppingCartRecipe,
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(amount_of_ingredients=Sum('amount'))
        return get_shopping_cart_file(ingredients, request.user.username)

    @action(
        detail=True,
        url_path='get-link',
        url_name='get-link',
        methods=('get',),
        permission_classes=(AllowAny,),
    )
    def short_link(self, request, pk):
        full_url = request.build_absolute_uri().rstrip('get-link/')
        serializer = ShortLinkSerializer(
            data={'full_url': full_url}
        )
        serializer.is_valid(raise_exception=True)
        url = serializer.create(
            validated_data=serializer.validated_data
        )
        parse_url = urlparse(full_url)
        base_url = parse_url.scheme + '://' + parse_url.netloc + '/s/'
        short_url = base_url + url.short_url
        return Response(
            {'short-link': short_url}, status=status.HTTP_200_OK
        )


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPagination
    filter_backends = (SearchFilter,)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        url_path='me/avatar',
        url_name='me-avatar',
        methods=('put',),
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        if not request.data:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserAvatarSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = User.objects.get(username=request.user.username)
        user.avatar = None
        user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        serializer = SubscriberSerializer(
            data={
                'user': user.id,
                'author': author.id,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        deleted_subscriber, _ = Subscriber.objects.filter(
            user=request.user,
            author=author,
        ).delete()

        if not deleted_subscriber:
            return Response(
                {f'Пользователя {author} не существует.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriptions = Subscriber.objects.filter(user=self.request.user)
        pagination = self.paginate_queryset(subscriptions)
        serializer = SubscriberSerializer(
            pagination,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)
