from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = models.ImageField(upload_to="img/users/", verbose_name="Аватар")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Отслеживаемый автор",
        related_name="following",
    )

    def __str__(self) -> str:
        return f"{self.user.username}||{self.author.username}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
