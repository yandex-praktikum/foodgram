import csv
from django.core.management.base import BaseCommand, CommandParser
from ingredient.models import Ingredient


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs) -> str | None:
        csv_file = kwargs["csv_file"]
        try:
            with open(csv_file, newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    name, measurement_unit = row[0], row[1]
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name, measurement_unit=measurement_unit
                    )

            self.stdout.write(self.style.SUCCESS(f"Ингредиенты успешно добавлены."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка: {e}"))
