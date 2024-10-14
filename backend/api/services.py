from datetime import date

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect

from food.models import IngredientRecipe, ShortLink


def shopping_cart(self, request, author):
    """Скачивание списка продуктов для выбранных рецептов пользователя."""
    sum_ingredients_in_recipes = IngredientRecipe.objects.filter(
        recipe__shopping_cart__author=author
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(
        amounts=Sum('amount', distinct=True)).order_by('amounts')
    today = date.today().strftime("%d-%m-%Y")
    shopping_list = f'Список покупок на: {today}\n\n'
    for ingredient in sum_ingredients_in_recipes:
        shopping_list += (
            f'{ingredient["ingredient__name"]} - '
            f'{ingredient["amounts"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )
    shopping_list += '\n\nFoodgram'
    filename = 'shopping_list.txt'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def get_long_url(short_url):
    """Получение полной ссылки"""
    try:
        object = ShortLink.objects.get(short_url__exact=short_url)
    except ShortLink.DoesNotExist:
        raise KeyError('No such url')
    return object.long_url


def redirection(request, short_url):
    """Переадресация по полной ссылке"""
    try:
        long_url = get_long_url(request.build_absolute_uri())
        return redirect(long_url)
    except Exception as e:
        raise HttpResponse(e.args)
