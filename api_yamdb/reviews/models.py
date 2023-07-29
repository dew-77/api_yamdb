from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import User


class Category(models.Model):
    name = models.TextField("Название", max_length=256)
    slug = models.SlugField("Краткое название", unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.TextField("Название", max_length=256)
    slug = models.SlugField("Краткое название", unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField("Название", max_length=256)
    year = models.IntegerField("Год выпуска")
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="titles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(Genre)
    description = models.TextField("Описание", null=True, blank=True)

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Review(models.Model):
    """Отзывы."""

    title = models.ForeignKey(
        Title,
        verbose_name="Произведение",
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True,
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Рейтинг",
        validators=[
            MinValueValidator(1, "Введенная оценка ниже допустимой"),
            MaxValueValidator(10, "Введенная оценка выше допустимой"),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("-pub_date",)
        constraints = (
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_title"
            ),
        )

    def __str__(self):
        return f"Отзыв на {self.author.username} на {self.title}"


class Comment(models.Model):
    """Комментарии."""

    review = models.ForeignKey(
        Review,
        verbose_name="Отзыв",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["pub_date"]

    def __str__(self):
        return f"{self.author}: {self.review.title}"
