from django.contrib.auth import get_user_model

from django.db import models


User = get_user_model()

LENG_MAX = 256



class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор'
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        'Назвение',
        max_length=LENG_MAX,
        db_index=True,
    )
    description = models.TextField(
        'Описание',
        db_index=True,
        max_length=LENG_MAX,
        blank=True,
    )