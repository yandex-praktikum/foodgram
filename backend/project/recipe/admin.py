from django.contrib import admin

from .models import Recipe, RecipeIngredient, ShoppingList, FavoriteRecipe


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "cooking_time",
        "author",
        "get_favorites",
        "get_ingredients",
    )
    search_fields = (
        "name",
        "author",
        "tags",
    )
    list_filter = ("author", "name", "tags")
    inlines = (IngredientInline,)

    def get_favorites(self, obj: Recipe) -> int:
        return obj.favorites.count()

    def get_ingredients(self, obj: Recipe):
        return ", ".join([ingredients.name for ingredients in obj.ingredients.all()])


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user", "recipe")


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user")
    list_filter = ("recipe", "user")
    search_fields = ("user",)
