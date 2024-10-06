"""URL-адреса.

backend/recipes/urls.py
"""

from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    UserViewSet,
)

auth_paths = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include(auth_paths)),
    path('', include(router.urls)),
]
