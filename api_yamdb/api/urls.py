from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupView,
    TitleViewSet,
    TokenView,
    UserViewSet
)


router = routers.DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"genres", GenreViewSet)
router.register(r"titles", TitleViewSet)
router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet, basename="title-reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet, basename="review-comments"
)
router.register(r"users", UserViewSet)

urlpatterns = [
    path("v1/auth/signup/", SignupView.as_view()),
    path("v1/auth/token/", TokenView.as_view()),
    path("v1/users/me/", UserViewSet.as_view(
        {"get": "me", "patch": "me"})),
    path("v1/users/<slug:username>/", UserViewSet.as_view(
        {"get": "retrieve", "patch": "update", "delete": "destroy"})),
    path("v1/", include(router.urls)),
]
