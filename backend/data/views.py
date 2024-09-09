from django.shortcuts import render
from rest_framework import viewsets
from users.permissions import IsOwnerOrReadOnly
from django.db.models import Avg
from .models import Recipe, Ingredients
from .serializers import RecipeSerializer, IngredientsSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    qqueryset = Recipe.objects.select_related("author")
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = RecipeSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    #filter_backends = (DjangoFilterBackend, filters.OrderingFilter, )
    #filterset_class = FilterForTitle
    #ordering_fields = ('name',)

    def get_queryset(self):
        queryset = self.queryset
        return queryset
    

class IngredientsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = IngredientsSerializer
    http_method_names = ["get"]
    ordering_fields = ('name')

    def get_queryset(self):
        queryset = self.queryset
        return queryset
