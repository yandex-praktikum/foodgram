from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

from .views import (IngredientViewSet, RecipeViewSet, ShortLinkAPIView,
                    TagViewSet)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    re_path(r'auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('recipes/<int:pk>/get-link/', ShortLinkAPIView.as_view()),
]
