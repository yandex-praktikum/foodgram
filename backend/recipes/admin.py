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
    UserFavoriteRecipe,
    UserShoppingCartRecipe,
)


class SubscriberInline(admin.TabularInline):
    model = Subscriber
    extra = 0
    fk_name = 'user'


class UserFavoriteRecipeInline(admin.TabularInline):
    model = UserFavoriteRecipe
    extra = 0


class UserShoppingCartRecipeInline(admin.TabularInline):
    model = UserShoppingCartRecipe
    extra = 0


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'is_staff'
    )
    list_display_links = (
        'username',
        'email',
    )
    inlines = (
        SubscriberInline,
        UserFavoriteRecipeInline,
        UserShoppingCartRecipeInline
    )
    search_fields = (
        'username',
        'email'
    )
    search_help_text = 'Поиск по `username` и `email`'


@admin.register(Ingredient)
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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'name',
        'cooking_time',
        'author',
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
                f'{obj.ingredient.name} - {obj.amount}'
                f'{obj.ingredient.measurement_unit}.'
            )
        return recipe_ingredients

    def get_recipe_tags(self, object):
        recipe_tags = [obj.name for obj in object.tags.all()]
        return recipe_tags


@admin.register(Subscriber)
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
        'author__username',
        'user__username'
    )


@admin.register(Tag)
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


@admin.register(UserFavoriteRecipe)
class UserFavoriteRecipeAdmin(admin.ModelAdmin):
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
        'user__username',
    )

    def get_recipe(self, object):
        return object.recipe


@admin.register(UserShoppingCartRecipe)
class UserShoppingCartRecipeAdmin(admin.ModelAdmin):
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
        'user__username',
    )

    def get_recipe(self, object):
        return object.recipe
