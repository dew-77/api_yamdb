from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Название роли')

    def __str__(self):
        return self.name


class User(AbstractUser):
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Роль'
    )

    def __str__(self):
        return self.username


class Review(models.Model):
    ...


class Comment(models.Model):
    ...


class Genre(models.Model):
    ...


class Category(models.Model):
    ...


class Title(models.Model):
    ...
