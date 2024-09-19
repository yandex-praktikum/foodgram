from django.contrib import admin

from recipes.models import (
    Ingredient,
    Tag,
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


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
