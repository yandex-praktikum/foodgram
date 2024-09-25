"""backend/recipes/views.py

"""

from django.contrib.auth import get_user_model
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
    Subscriber,
    Tag,
)
from recipes.paginations import LimitPagination
from recipes.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    SubscriberSerializer,
    TagSerializer,
    UserSerializer,
    UserAvatarSerializer,
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
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']


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
