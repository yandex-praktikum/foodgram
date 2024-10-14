from django.contrib.auth.models import AbstractUser
from django.db import models

from . import constants


class User(AbstractUser):
    """
    Кастомизированная модель пользователя.
    Регистрация с помощью email.
    """
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    email = models.EmailField(
        'email-адрес',
        unique=True
    )
    role = models.CharField(
        max_length=15,
        choices=constants.ROLES,
        default=constants.USER,
        verbose_name='Пользовательская роль'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )
    USERNAME_FIELD = 'email'
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default=None
    )
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == constants.ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == User.USER

    def __str__(self):
        return self.username
