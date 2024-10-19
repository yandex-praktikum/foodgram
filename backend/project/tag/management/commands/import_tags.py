import csv
from django.core.management.base import BaseCommand, CommandParser
from tag.models import Tag


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs) -> str | None:
        csv_file = kwargs["csv_file"]
        try:
            with open(csv_file, newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    name, slug = row[0], row[1]
                    tag, created = Tag.objects.get_or_create(
                        name=name, slug=slug
                    )
                    

            self.stdout.write(self.style.SUCCESS(f"Теги успешно добавлены."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка: {e}"))

