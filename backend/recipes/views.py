"""backend/recipes/views.py

"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from rest_framework import filters, mixins, viewsets


from recipes.filters import RecipeFilter
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
)
from recipes.permissions import IsAuthorOrReadOnly, IsAdmin
from recipes.serializers import (
    IngredientReadSerializer,
    TagReadSerializer,
    RecipeReadSerializer,
    UserReadSerializer
)

User = get_user_model()


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
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    permission_classes = (IsAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ['username']
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role, partial=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
