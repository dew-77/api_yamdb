from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .validators import validate_pattern
from reviews.models import Category, Comment, Genre, Review, Title
from core.models import User


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для самостоятельной регистрации пользователей."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate(self, data):
        email = data.get("email")
        username = data.get("username")

        if User.objects.filter(email=email, username=username).exists():
            user = User.objects.get(email=email, username=username)
            return user

        if username == "me":
            raise serializers.ValidationError(
                "Нельзя использовать me в качестве юзернейма!"
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Пользователь c указанным email уже существует"
            )

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "Пользователь c указанным юзернеймом уже существует"
            )

        validate_pattern(username)

        return super().validate(data)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
        ]


class ConfirmSerializer(serializers.ModelSerializer):
    """Сериализатор для подтверждения регистрации пользователей."""

    confirmation_code = serializers.CharField(max_length=10)
    username = serializers.CharField(max_length=150)

    def validate(self, data):
        confirmation_code = data.get("confirmation_code")
        username = data.get("username")

        validate_pattern(username)

        user = get_object_or_404(User, username=username)

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Неверный код подтверждения")
        return super().validate(data)

    class Meta:
        model = User
        fields = [
            "username",
            "confirmation_code",
        ]


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и добавления пользователей."""

    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(max_length=254, required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(
        choices=User.ROLES, default="user"
    )

    def validate(self, data):
        username = data.get("username")
        email = data.get("email")

        if self.context["request"].method == "POST":
            if not username:
                raise serializers.ValidationError(
                    "Поле username обязательно"
                )
            if not email:
                raise serializers.ValidationError(
                    "Поле email обязательно"
                )

        if username:
            validate_pattern(username)

        if username == "me":
            raise serializers.ValidationError(
                "Нельзя использовать me в качестве юзернейма!"
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Пользователь c указанным email уже существует"
            )

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "Пользователь c указанным юзернеймом уже существует"
            )

        return super().validate(data)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        ]


class MePatchSerializer(serializers.ModelSerializer):
    """Сериализатор для PATCH-запросов к своему профилю."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)

    def validate(self, data):
        username = data.get("username")
        if username:
            validate_pattern(username)
        return data

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "bio"]


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для GET-запросов к произведениям."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id", "name", "year",
            "category", "genre", "description",
            "rating"
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = ("id", "name", "year", "category", "genre", "description")

    def validate(self, data):
        if "year" in data:
            if int(data["year"]) > datetime.today().year:
                raise serializers.ValidationError(
                    "Год выпуска не может быть больше текущего"
                )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    def validate(self, data):
        author = self.context["request"].user
        title_id = self.context["view"].kwargs.get("title_id")
        if self.context["request"].method == "POST":
            if Review.objects.filter(
                author=author, title_id=title_id
            ).exists():
                raise serializers.ValidationError(
                    "Ha одно произведение можно оставить только 1 отзыв!")
        return data

    class Meta:
        model = Review
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("review", "author")
