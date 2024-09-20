from django.contrib import admin

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
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
    list_display = (
        'pk',
        'name',
        'author',
        'in_favorites'
    )
    list_display_links = (
        'name',
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
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite_recipe.count()


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
