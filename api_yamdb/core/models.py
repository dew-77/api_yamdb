from django.db import models


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
