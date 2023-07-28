import re
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from core.models import Category, Genre, Title, User


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

        pattern = r"^[\w.@+-]+$"
        if not re.match(pattern, username):
            raise serializers.ValidationError("Некорректный формат username")

        return data

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

        pattern = r"^[\w.@+-]+$"
        if not re.match(pattern, username):
            raise serializers.ValidationError("Некорректный формат username")

        user = get_object_or_404(User, username=username)

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Неверный код подтверждения")
        return data

    class Meta:
        model = User
        fields = [
            "username",
            "confirmation_code",
        ]


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и добавления пользователей."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(
        choices=["user", "moderator", "admin"], default="user"
    )

    def validate(self, data):
        username = data.get("username")
        email = data.get("email")

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

        pattern = r"^[\w.@+-]+$"
        if not re.match(pattern, username):
            raise serializers.ValidationError("Некорректный формат username")

        return data

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
            pattern = r"^[\w.@+-]+$"
            if not re.match(pattern, username):
                raise serializers.ValidationError(
                    "Некорректный формат username"
                )

        return data

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "bio"]


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра, изменения, удаления пользователя."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(
        choices=["user", "moderator", "admin"], default="user"
    )

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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        model = Title
        fields = ("id", "name", "year", "category", "genre", "description")


class TitleWriteSerializer(serializers.ModelSerializer):
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
