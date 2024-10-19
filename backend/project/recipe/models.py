from django.db import models

from ingredient.models import Ingredient
from tag.models import Tag
from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="recipes",
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    image = models.ImageField(upload_to="img/recipes/", verbose_name="Картинка")
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(Ingredient, verbose_name="Ингридиенты")
    tags = models.ManyToManyField(Tag, verbose_name="Тэги")
    cooking_time = models.PositiveSmallIntegerField(verbose_name="Время приготовления")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания рецепта"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления рецепта"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингридиент"
    )
    amount = models.PositiveIntegerField(verbose_name="Количество", default=1)

    def __str__(self) -> str:
        return f"{self.recipe}-{self.ingredient}:{self.amount}"

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorites",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self) -> str:
        return f"{self.user} - {self.recipe}"

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name='shopping_list'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self) -> str:
        return f"Список покупок для {self.user} - {self.recipe}"

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        unique_together = ("user", "recipe")
