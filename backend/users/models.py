from django.contrib.auth.models import AbstractUser
from django.db import models


LENG_MAIL = 254
LENG_USER = 150


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    USER_ROLES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField(
        'Email', 
        max_length=LENG_MAIL,
        unique=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=LENG_USER,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=LENG_USER,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LENG_USER,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self == self.ADMIN or self.is_superuser
    
    @property
    def is_user(self):
        return self == self.USER
