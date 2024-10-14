from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import (IsAdminIsAuthorOrReadOnly, IsAdminIsAuthor)
from api.serializers import SubscribeListCreateDeleteSerializer
from food.models import Subscribe
from users.models import User
from users.serializers import (SetPasswordSerrializer,
                               UserListRetrieveSerializer, UserSerializer,
                               UserUpdateAvatarSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для модели пользователей."""
    queryset = User.objects.all()
    permission_classes = (IsAdminIsAuthor,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'me']:
            return UserListRetrieveSerializer
        elif self.action == 'avatar':
            return UserUpdateAvatarSerializer
        elif self.action == 'set_password':
            return SetPasswordSerrializer
        elif self.action in ['subscriptions', 'subscribe']:
            return SubscribeListCreateDeleteSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=kwargs['pk'])
        seriazier = self.get_serializer_class()(
            user,
            context=self.get_serializer_context()
        )
        return Response(seriazier.data)

    @action(
        methods=('GET',),
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer_class()(
            request.user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('PUT', 'DELETE'),
        detail=False,
        url_path='me/avatar',
        url_name='me/avatar',
        permission_classes=(IsAdminIsAuthorOrReadOnly,
                            IsAuthenticated),
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = self.get_serializer_class()(
                request.user,
                data=request.data,
                context=self.get_serializer_context()
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(username=request.user)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('POST',),
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data=request.data,
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response('Пароль успешно изменен',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('GET',),
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriptions = Subscribe.objects.filter(user=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer_class()(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('POST', 'DELETE',),
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = request.user

        if request.method == 'POST':
            serializer = self.get_serializer_class()(
                data=request.data,
                context={'request': request, 'author': author}
            )

            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Страница не найдена'},
                            status=status.HTTP_404_NOT_FOUND)

        # method DELETE
        if Subscribe.objects.filter(author=author, user=user).exists():
            Subscribe.objects.get(author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'Подписка не найдена'},
                        status=status.HTTP_400_BAD_REQUEST)
