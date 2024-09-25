from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Subscriber,
    Tag,
    User,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
)


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'is_staff'
    )
    list_display_links = (
        'username',
        'email',
    )
    search_fields = (
        'username',
        'email'
    )
    search_help_text = 'Поиск по `username` и `email`'


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


class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)


class RecipeTagAdmin(admin.StackedInline):
    model = RecipeTag
    autocomplete_fields = ('tag',)


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'pk',
        'name',
        'author',
        'image',
        'text',
        'cooking_time',
        'get_favorite_count',
        'get_recipe_ingredients',
        'get_recipe_tags',
    )
    list_display_links = (
        'name',
        'author',
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )
    readonly_fields = (
        'get_favorite_count',
        'get_recipe_ingredients',
        'get_recipe_tags',
    )
    search_fields = (
        'name',
        'author__username',
        'tags__name'
    )
    inlines = (
        RecipeIngredientAdmin,
        RecipeTagAdmin
    )

    def get_favorite_count(self, obj):
        return obj.favorite_recipe.count()

    def get_recipe_ingredients(self, object):
        recipe_ingredients = []
        for obj in object.recipe.all():
            recipe_ingredients.append(
                f'{obj.ingredient.name} - {obj.quantity}'
                f'{obj.ingredient.measurement_unit}.'
            )
        return recipe_ingredients

    def get_recipe_tags(self, object):
        recipe_tags = []
        for obj in object.tags.all():
            recipe_tags.append(obj.name)
        return recipe_tags


class SubscriberAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'user',
        'author'
    )
    list_filter = (
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author',
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


class UserShoppingCartRecipesAdmin(admin.ModelAdmin):
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
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserFavoriteRecipes, UserFavoriteRecipesAdmin)
admin.site.register(UserShoppingCartRecipes, UserShoppingCartRecipesAdmin)
