from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated
)
from rest_framework.response import Response
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
    UsersSerializer,
)
from .viewsets import CreateListDestroyViewSet
from .paginators import UsersPagination
from core.services import send_confirmation_email, generate_confirmation_code


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


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для взаимодействия с моделью пользователя.
    """

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    permission_classes = [IsAdmin]
    pagination_class = UsersPagination
    lookup_field = "username"

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        """
        Обработчик GET и PATCH запросов к users/me/
        """
        if request.method == "GET":
            serializer = UsersSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PATCH":
            serializer = MePatchSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action in [
            "update", "list", "retrieve", "create", "destroy"
        ]:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


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

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == "GET":
            queryset = queryset.annotate(
                rating=Avg("reviews__score")).order_by("-id")
        return queryset


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
