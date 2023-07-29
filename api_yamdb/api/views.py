import random
import string

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User

from .permissions import (
    IsAdmin,
    ReadOnly,
    IsAuthorOrReadOnly,
    IsModeratorOrAdminOrReadOnly
)
from .serializers import (
    CategorySerializer,
    ConfirmSerializer,
    CommentSerializer,
    GenreSerializer,
    MePatchSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer,
    UsersSerializer,
)
from .viewsets import CreateListDestroyViewSet


def generate_confirmation_code(length=6):
    """Генерирует случайный код подтверждения заданной длины."""
    characters = string.digits
    confirmation_code = "".join(
        random.choice(characters) for _ in range(length)
    )
    return confirmation_code


def send_confirmation_email(email, confirmation_code):
    """Отправляет email с кодом подтверждения на указанный адрес."""
    subject = "Подтверждение регистрации"
    message = render_to_string(
        "confirmation_email.html", {"code": confirmation_code}
    )
    from_email = "yamdb@yamdb.com"
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    print(f"Отправлено письмо с кодом {confirmation_code} на адрес {email}.")


class UsersPagination(PageNumberPagination):
    """Пагинатор для UsersView."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class SignupView(generics.CreateAPIView):
    """Generic для самостоятельной регистрации пользователей."""

    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if isinstance(user, User):
            return Response(
                SignupSerializer(user).data, status=status.HTTP_200_OK
            )
        else:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_200_OK, headers=headers
            )

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_unusable_password()
        user.confirmation_code = generate_confirmation_code()
        user.save()
        send_confirmation_email(user.email, user.confirmation_code)


class TokenView(generics.CreateAPIView):
    """Generic для подтверждения и получения токена."""

    queryset = User.objects.all()
    serializer_class = ConfirmSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        user = User.objects.get(username=username)
        user.is_confirmed = True
        user.save()
        access = AccessToken.for_user(user)
        token = {
            "access": str(access),
        }

        return Response(token, status=status.HTTP_200_OK)


class UsersView(generics.ListCreateAPIView):
    """
    Generic для:
    1) Просмотра пользователей
    2) Создания пользователя администратором.
    """

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    permission_classes = [IsAdmin]
    pagination_class = UsersPagination


class MeView(APIView):
    """Generic для просмотра и редактирования своего профиля."""

    serializer_class = MePatchSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = MePatchSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserView(APIView):
    """Generic для просмотра и редактирования конкретного пользователя."""

    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def patch(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = self.serializer_class(
            user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, username):
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(CreateListDestroyViewSet):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin | ReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(CreateListDestroyViewSet):
    """ViewSet для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdmin | ReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreFilter(filters.BaseFilterBackend):
    """Фильтр для поиска по slug жанра."""

    def filter_queryset(self, request, queryset, view):
        genre_slug = request.query_params.get("genre")
        if genre_slug:
            genre = get_object_or_404(Genre, slug=genre_slug)
            queryset = queryset.filter(genre=genre)
        return queryset


class CategoryFilter(filters.BaseFilterBackend):
    """Фильтр для поиска по slug категории."""

    def filter_queryset(self, request, queryset, view):
        category_slug = request.query_params.get("category")
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        return queryset


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений."""

    queryset = Title.objects.all()
    permission_classes = [IsAdmin | ReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, GenreFilter, CategoryFilter)
    filterset_fields = (
        "name",
        "year",
    )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для оценок."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrReadOnly | IsModeratorOrAdminOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(title_id=self.kwargs["title_id"])

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(
            author=self.request.user, title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly | IsModeratorOrAdminOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(
            Review, pk=self.kwargs.get("review_id"),
            title_id=self.kwargs.get("title_id")
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get("review_id"),
            title=self.kwargs.get("title_id")
        )
        serializer.save(
            author=self.request.user, review=review
        )
