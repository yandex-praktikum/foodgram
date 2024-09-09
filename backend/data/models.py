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
    slug = models.CharField(
        verbose_name='Слаг тега',
        max_length=LENG_MAX,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

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

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

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
        'Название',
        max_length=LENG_MAX,
        db_index=True,
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='data/images',
        null=True,
        default=None,
    )
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
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    cook_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        default=0,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name
    
    


