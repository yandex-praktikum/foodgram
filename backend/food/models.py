from random import choices

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from api import constants
from users.models import User


class Ingredient(models.Model):
    """Модель ингридиентов для рецептов."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=constants.MAX_LEN_INGREDIENT_NAME,
        db_index=True,
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=constants.MAX_LEN_INGREDIENT_MEASUREMENT_UNIT,
        help_text='Введите единицу измерения'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    """Модель тегов для рецептов с предустановленным выбором."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=constants.MAX_LEN_TAG_NAME,
        help_text='Введите название тега'
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=constants.MAX_LEN_TAG_SLUG,
        default=None,
        help_text='Укажите уникальный слаг',
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Название тега',
        help_text='Выберите tag'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipies',
        help_text='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиент'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=constants.MAX_LEN_RECIPE_NAME,
        help_text='Введите название рецепта',
        db_index=True
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='media/',
        help_text='Добавьте изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Опишите приготовление рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Минимальное время приготовления'
            )
        ],
        help_text='Укажите время приготовления рецепта в минутах'
    )

    class Meta:
        ordering = ['-id']
        default_related_name = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe',
            )
        ]


class IngredientRecipe(models.Model):
    """Вспомогательная модель, связывающая ингредиенты и рецепты"""
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        help_text='Укажите ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Минимальное количество ингредиентов 1'
            )
        ],
        verbose_name='Количество',
        help_text='Укажите количество ингредиента'
    )

    class Meta:
        verbose_name = 'Cостав рецепта'
        verbose_name_plural = 'Состав рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class ShoppingCart(models.Model):
    """Модель списка покупок пользователя."""
    author = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт для приготовления',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт для приготовления'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_cart'
            )
        ]

    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""
    author = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта')
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe}'


class Subscribe(models.Model):
    """Модель подписок на авторов рецептов."""
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
        help_text='Текущий пользователь'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Подписка',
        related_name='followed',
        on_delete=models.CASCADE,
        help_text='Подписаться на автора рецепта(ов)'
    )

    class Meta:
        verbose_name = 'Мои подписки'
        verbose_name_plural = 'Мои подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_following'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'


class ShortLink(models.Model):
    """Модель коротких ссылок."""
    long_url = models.URLField(unique=True)
    short_url = models.URLField(
        verbose_name='Короткая ссылка',
        db_index=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created_at',)

    def save(self, *args, **kwargs) -> None:
        """Генерация уникального короткого url."""
        prefix = '/'.join(self.long_url.split('/')[:3]) + '/'
        while True:
            self.short_url = prefix + ''.join(
                choices(
                    constants.CHARACTERS,
                    k=constants.MAX_LEN_SHORT_LINK
                )
            ) + '/'
            if not ShortLink.objects.filter(
                short_url=self.short_url
            ).exists():
                break
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.long_url}   *brrr* -->   {self.short_url}'
