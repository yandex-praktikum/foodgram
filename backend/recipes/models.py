"""Модели.

backend/recipes/models.py
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import (
    EmailValidator, MinValueValidator, MaxValueValidator
)
from django.db import models

from recipes.constants import (
    NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    MIN_VALUE_VALIDATOR,
    SLUG_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    BIO_MAX_LENGTH,
    ROLE_LENGTH_LIMIT,
    ROLE_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
)
from recipes.validators import username_validator


class UserRole(models.TextChoices):
    USER = 'user', 'пользователь'
    ADMIN = 'admin', 'администратор'


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=(
            f'Имя пользователя, не более {USERNAME_MAX_LENGTH} символов.',
            'Допустимые символы: буквы, цифры и @/./+/-/_'
        ),
        validators=[
            UnicodeUsernameValidator(
                message=(
                    'Имя пользователя содержит недопустимые символы. '
                    'В имени пользователя допускается использовать буквы, '
                    'цифры и символы _.@+-'
                )
            ),
            username_validator
        ]
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        help_text=(
            f'Адрес электронной почты, не более {EMAIL_MAX_LENGTH} символов'
        ),
    )
    first_name = models.CharField(
        verbose_name='Имя Отчество',
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=True,
        help_text=(
            f'Имя Отчество, не более {FIRST_NAME_MAX_LENGTH} символов'
        ),
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LAST_NAME_MAX_LENGTH,
        blank=True,
        help_text=(
            f'Фамилия, не более {LAST_NAME_MAX_LENGTH} символов'
        ),
    )
    bio = models.CharField(
        verbose_name='Биография',
        max_length=BIO_MAX_LENGTH,
        blank=True,
        help_text=(
            f'Биография, не более {BIO_MAX_LENGTH} символов'
        ),
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=PASSWORD_MAX_LENGTH,
        help_text=(
            f'Пароль, не более {PASSWORD_MAX_LENGTH} символов'
        ),
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=ROLE_MAX_LENGTH,
        help_text=(
            f'Роль, не более {ROLE_MAX_LENGTH} символов'
        ),
        choices=UserRole.choices,
        default=UserRole.USER
    )

    REQUIRED_FIELDS = ['email', ]

    class Meta(AbstractUser.Meta):
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.role[:ROLE_LENGTH_LIMIT]})'

    @property
    def is_user(self):
        return self.role == UserRole.USER

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser


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


class UserFavoriteRecipes(models.Model):
    """Избранные рецепты пользователя.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite',
        verbose_name='Избранное пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное пользователя'
        verbose_name_plural = 'Избранное пользователя'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
