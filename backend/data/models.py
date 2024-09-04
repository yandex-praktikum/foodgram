from django.contrib.auth import get_user_model

from django.db import models



User = get_user_model()

LENG_MAX = 256


class Tag(models.Model):
    name = models.CharField(
        'Тег',
        max_length=LENG_MAX,
        unique=True,
    )

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        'Название',
        max_length=LENG_MAX,
        db_index=True,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=LENG_MAX,
        db_index=True,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        verbose_name='Автор',
        related_name='recipes',
        to=User,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        'Назвение',
        max_length=LENG_MAX,
        db_index=True,
    )
    #image = models.ImageField(
    #    upload_to='data/images',
    #    null=True,
    #    default=None,
    #)
    description = models.TextField(
        'Описание',
        db_index=True,
        max_length=LENG_MAX,
        blank=True,
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты',
        related_name='recipes',
        to=Ingredients,
    )
    tags = models.ManyToManyField(
        verbose_name='Тег',
        related_name='tags',
        to=Tag,
    )

    def __str__(self):
        return self.name


