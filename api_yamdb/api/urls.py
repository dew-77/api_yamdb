from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    GenreViewSet,
    MeView,
    SignupView,
    TitleViewSet,
    TokenView,
    UsersView,
    UserView,
)

router = routers.DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"genres", GenreViewSet)
router.register(r"titles", TitleViewSet)

urlpatterns = [
    path("v1/auth/signup/", SignupView.as_view()),
    path("v1/auth/token/", TokenView.as_view()),
    path("v1/users/", UsersView.as_view()),
    path("v1/users/me/", MeView.as_view()),
    path("v1/users/<slug:username>/", UserView.as_view()),
    path("v1/", include(router.urls)),
]
