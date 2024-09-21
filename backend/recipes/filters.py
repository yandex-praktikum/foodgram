"""backend/recipes/filters.py
"""
from django_filters import CharFilter, ModelChoiceFilter, FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import (
    Recipe,
)


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        method='filters_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filters_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filters_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def filters_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    search_param = 'name'
