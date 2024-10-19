from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    measurement_unit = models.CharField(max_length=32, verbose_name="Единица измерения")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания ингредиента"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления ингредиента"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
