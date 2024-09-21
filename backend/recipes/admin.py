from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    User,
    UserFavoriteRecipes,
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_display_links = (
        'name',
    )
    list_filter = (
        'name',
    )
    search_fields = (
        'name',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    list_display_links = (
        'name',
    )
    list_filter = (
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'pk',
        'name',
        'author',
        'in_favorites'
    )
    list_display_links = (
        'name',
        'author',
    )
    list_editable = (
        #'name',
        #'cooking_time',
        #'text',
        #'tags',
        #'image',
        #'author'
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )
    readonly_fields = (
        'in_favorites',
    )
    search_fields = (
        'name',
        'author',
        'tags'
    )

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite_recipe.count()


class UserFavoriteRecipesAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'pk',
        'user',
        'get_recipe',
    )
    list_filter = (
        'user',
    )
    search_fields = (
        'user',
    )

    def get_recipe(self, object):
        return object.recipe


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(UserFavoriteRecipes, UserFavoriteRecipesAdmin)
admin.site.register(User, UserAdmin)
