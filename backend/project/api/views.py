from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import (
    Recipe,
    RecipeIngredient,
    ShoppingList,
    FavoriteRecipe,
)
from users.models import User, Follow
from tag.models import Tag
from ingredient.models import Ingredient
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    FavoriteSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    AuthorSerializer,
    UserSerializer,
)
from .paginations import CustomPagination
from .permissions import IsAuthorOrReadOnly

from typing import Sequence


class IngredientView(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
    serializer_class = IngredientSerializer
    search_fields = ("^name",)
    pagination_class = None


class TagView(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class RecipeView(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = RecipeWriteSerializer
    filterset_class = RecipeFilter

    def get_serializer_class(
        self,
    ) -> RecipeReadSerializer | RecipeWriteSerializer:
        if self.action in ["create", "update", "partial_update"]:
            return RecipeWriteSerializer
        else:
            return RecipeReadSerializer

    def create_file(self, ingredients: Sequence[RecipeIngredient]) -> Response:
        shopping_list = "Список покупок:"
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}"
            )
        file = "shopping_list.txt"
        response = Response(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None) -> Response:
        recipe = self.get_object()
        short_link = f"https://foodgram.example.org/s/{recipe.id}"
        return Response({"short-link": short_link})

    @action(
        detail=True,
        methods=["post"],
        url_path="favorite",
        permission_classes=[IsAuthenticated],
    )
    def create_favorite(self, request: Request, pk=None) -> Response:
        context = {"request": request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {"user": request.user.id, "recipe": recipe.id}
        serializer = FavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @create_favorite.mapping.delete
    def delete_favorite(self, request: Request, pk):
        get_object_or_404(
            FavoriteRecipe,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk),
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request: Request) -> Response:
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppinglist__user=request.user
            )
            .order_by("ingredient__name")
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        return self.create_file(ingredients)

    @action(
        detail=True,
        methods=["post"],
        url_path="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def create_shopping_cart(self, request: Request, pk) -> Response:
        recipe = get_object_or_404(Recipe, id=pk)
        data = {"user": request.user.id, "recipe": recipe.id}
        context = {"request": request}
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @create_shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingList,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk),
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserView(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request: Request, id) -> Response:
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == "POST":
            serializer = AuthorSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request: Request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = AuthorSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["put"],
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request: Request) -> Response:
        user: User = request.user
        serializer = AuthorSerializer(
            user, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
