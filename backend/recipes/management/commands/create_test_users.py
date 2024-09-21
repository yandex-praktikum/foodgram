"""Создание тестовых пользователей.

create_test_users.py
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание тестовых пользователей.'

    def add_arguments(self, parser):
        parser.add_argument(
            'total',
            type=int,
            help='Количество создаваемых пользователей.')
        parser.add_argument(
            '-P', '--prefix',
            type=str,
            help='Префикс имени пользователя.',
        )
        parser.add_argument(
            '-A', '--admin',
            action='store_true',
            help='Назначить права администратора.'
        )

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        prefix = kwargs['prefix']
        admin = kwargs['admin']

        for i in range(total):
            if prefix:
                username = f'{prefix}-{i}'
            else:
                username = f'test_user-{i}'
            try:
                if admin:
                    User.objects.create_superuser(
                        username=username,
                        email=f'{username}@localhost.loc',
                        password='1234567890'
                    )
                else:
                    User.objects.create_user(
                        username=username,
                        email=f'{username}@localhost.loc',
                        password='1234567890'
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Пользователь {username} создан!'
                    )
                )
            except User.Exist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Пользователь {username} не создан.'
                    )
                )
