"""Импорт ингредиентов из csv-файла в базу данных.

import_ingredients_from_csv-file.py
"""

import csv

from django.core.management.base import BaseCommand
from progress.bar import IncrementalBar

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Импорт ингредиентов из csv-файла в базу данных."

    def add_arguments(self, parser):
        parser.add_argument('-P', '--path', type=str, help='Путь csv-файла.')

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                row_count = sum(1 for row in file)
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                incremental_bar = IncrementalBar(
                    'Импорт ингредиентов из csv-файла в базу данных:',
                    max=row_count
                )
                next(reader)
                for row in reader:
                    incremental_bar.next()
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
                incremental_bar.finish()
            self.stdout.write(
                self.style.SUCCESS(
                    'Ингредиенты успешно импортированы из csv-файла '
                    f'{path} в базу данных.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("Не указан путь csv-файла.")
            )
