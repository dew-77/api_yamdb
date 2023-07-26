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
    """Отзывы."""
    title = models.ForeignKey(
        Title,
        verbose_name="Произведение",
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Рейтинг",
        validators=[
            MinValueValidator(1, "Введенная оценка ниже допустимой"),
            MaxValueValidator(10, "Введенная оценка выше допустимой")
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name="unique_author_title"
            ),
        )
    
    def __str__(self):
        return self.name


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


class Comment(models.Model):
    """Комментарии."""
    review = models.ForeignKey(
        Review,
        verbose_name="Отзыв",
        on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="comments"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['pub_date']

    def __str__(self):
        return self.name
