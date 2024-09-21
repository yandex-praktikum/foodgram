"""backend/recipes/urls.py

"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    UserViewSet,
)


router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
]
