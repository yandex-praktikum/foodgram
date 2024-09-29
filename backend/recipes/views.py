"""backend/recipes/views.py

"""

from io import BytesIO
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
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

from foodgram_backend.settings import BASE_DIR
from recipes.filters import (
    IngredientFilter,
    RecipeFilter,
)
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShortLink,
    Subscriber,
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
    UserFavoriteRecipeSerializer,
    UserShoppingCartRecipe
)

User = get_user_model()


class IngredientViewSet(ReadOnlyModelViewSet):
    """Маршрутизация ингридиентов.
    """
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
    """Маршрутизация тегов.
    """
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
            return UserFavoriteRecipeSerializer
        elif self.action == 'shopping_cart':
            return UserShoppingCartRecipe
        return RecipeCUDSerializer

    def post_to_list(self, request, pk):
        serializer = self.get_serializer(data=dict(recipe=pk))
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_to_list(request, pk, model):
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
        return self.post_to_list(
            request,
            pk,
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_to_list(
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
        return self.post_to_list(
            request,
            pk,
        )

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        return self.delete_to_list(
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
        path_to_fonts = BASE_DIR / 'data/fonts/FreeSans.ttf'
        buffer = BytesIO()
        pdf_file = canvas.Canvas(buffer)
        pdfmetrics.registerFont(
            TTFont(
                'FreeSans',
                path_to_fonts,
            )
        )
        pdf_file.setFont('FreeSans', 15)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(amount_of_ingredients=Sum('amount'))

        pdf_file.drawString(100, 750, 'Ваш список покупок')

        y = 700
        for ingredient in ingredients:
            pdf_file.drawString(
                100,
                y,
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount_of_ingredients"]} '
                f'{ingredient["ingredient__measurement_unit"]}',
            )
            y -= 20

        pdf_file.showPage()
        pdf_file.save()
        buffer.seek(0)
        response = FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_list.pdf'
        )
        return response

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
        serializer.save(user=request.user)
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
        followings = Subscriber.objects.filter(user=self.request.user)
        pagination = self.paginate_queryset(followings)
        serializer = SubscriberSerializer(
            pagination,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)
