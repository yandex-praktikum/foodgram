"""Модели.

backend/recipes/models.py
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator
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
)
from recipes.validators import username_validator


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=(
            f'Имя пользователя, не более {USERNAME_MAX_LENGTH} символов.',
            'Допустимые символы: буквы, цифры и @/./+/-/_'
        ),
        error_messages={
            'unique': 'Имя пользователя уже используется!'
        },
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
        error_messages={
            'unique': 'Адрес электронной почты уже используется!'
        },
    )
    first_name = models.CharField(
        verbose_name='Имя Отчество',
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=False,
        help_text=(
            f'Имя Отчество, не более {FIRST_NAME_MAX_LENGTH} символов'
        ),
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LAST_NAME_MAX_LENGTH,
        blank=False,
        help_text=(
            f'Фамилия, не более {LAST_NAME_MAX_LENGTH} символов'
        ),
    )
    avatar = models.ImageField(
        verbose_name='Аватар пользователя',
        blank=True,
        null=True,
        upload_to='media/users/avatars/',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи',
        ordering = [
            'username',
            'email',
        ]

    def __str__(self):
        return f'{self.username}'


class Subscriber(models.Model):
    """Подписчик.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='subscribing',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscriber',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscriber'
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}.'


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
        through='RecipeTag',
        through_fields=('recipe', 'tag'),
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
        related_name='recipes_with_ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент'
    )
    quantity = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE_VALIDATOR,
                f'Минимальное количество ингредиентов: {MIN_VALUE_VALIDATOR}'
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.ingredient.name} - '
            f'{self.quantity} '
            f'{self.ingredient.measurement_unit}'
        )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_with_tag',
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_combination_recipe_tag'
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.tag.name} - '
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
        verbose_name_plural = 'Избранное пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class UserShoppingCartRecipes(models.Model):
    """Рецепты из пользовательской корзины.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Владелец корзины',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_shopping_cart',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'Корзина пользователя с рецептом'
        verbose_name_plural = 'Корзины пользователей с рецептами'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shopping_cart_with_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
