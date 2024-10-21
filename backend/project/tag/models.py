from django.db import models


class Tag(models.Model):
    name = models.CharField(
        max_length=255, verbose_name="Название", unique=True
    )
    slug = models.SlugField(verbose_name="Slug", max_length=55, unique=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания тега"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления тега"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
