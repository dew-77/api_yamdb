from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = (
        ("user", "Аутентифицированный пользователь"),
        ("moderator", "Модератор"),
        ("admin", "Администратор"),
    )

    role = models.CharField(
        max_length=20, choices=ROLES, default="user", verbose_name="Роль"
    )

    email = models.EmailField(max_length=254, unique=True)

    bio = models.TextField(blank=True, null=True, verbose_name="Био")

    confirmation_code = models.CharField(max_length=10, blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return self.username
