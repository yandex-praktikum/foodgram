"""backend/recipes/models.py

"""
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (
    NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    MIN_VALUE_VALIDATOR,
    SLUG_MAX_LENGTH,
)

User = get_user_model()

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


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=NAME_MAX_LENGTH,
        db_index=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=[
            MinValueValidator(
                MIN_VALUE_VALIDATOR,
                f'Минимальное значение: {MIN_VALUE_VALIDATOR}'
            )
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE_VALIDATOR,
                f'Минимальное значение: {MIN_VALUE_VALIDATOR}'
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination'
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.ingredient.name} - '
            f'{self.quantity} '
            f'{self.ingredient.measurement_unit}'
        )
