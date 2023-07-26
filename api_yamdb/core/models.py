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


class Category(models.Model):
    name = models.TextField("Название")
    slug = models.SlugField("Краткое название", unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.TextField("Название")
    slug = models.SlugField("Краткое название", unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField("Название")
    year = models.DateTimeField("Год выпуска", auto_now_add=True)
    category = models.ForeignKey(
        Category,
        verbose_name="Произведения",
        related_name="titles",
        on_delete=models.SET_NULL,
        null=True,
    )
    genre = models.ManyToManyField(Genre, through="GenreTitle")

    def __str__(self):
        return self.name
