"""backend/recipes/models.py

"""
from django.db import models

from recipes.constants import (
    NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    SLUG_MAX_LENGTH,
)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name
