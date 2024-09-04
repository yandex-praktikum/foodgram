from django.contrib.auth import get_user_model

from django.db import models



User = get_user_model()

LENG_MAX = 256



class Recipe(models.Model):
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