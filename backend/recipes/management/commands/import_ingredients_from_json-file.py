"""Импорт ингредиентов из json-файла в базу данных.

import_ingredients_from_json-file.py
"""

import json

from django.core.management.base import BaseCommand
from progress.bar import IncrementalBar

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Импорт ингредиентов из json-файла в базу данных."

    def add_arguments(self, parser):
        parser.add_argument('-P', '--path', type=str, help='Путь json-файла.')

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                ingredients = json.loads(file_content)
            incremental_bar = IncrementalBar(
                'Импорт ингредиентов из json-файла в базу данных:',
                max=len(ingredients)
            )
            for ingredient in ingredients:
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
                incremental_bar.next()
            incremental_bar.finish()
            self.stdout.write(
                self.style.SUCCESS(
                    'Ингредиенты успешно импортированы из json-файла '
                    f'{path} в базу данных.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("Не указан путь json-файла.")
            )
