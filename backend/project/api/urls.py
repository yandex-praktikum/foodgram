from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeView, TagView, IngredientView, UserView

app_name = "api"


router = DefaultRouter()
router.register("ingredients", IngredientView, basename="ingredients")
router.register("tags", TagView, basename="tags")
router.register("recipes", RecipeView, basename="recipes")
router.register("users", UserView, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
