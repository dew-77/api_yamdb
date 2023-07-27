from django.urls import path
from .views import SignupView, TokenView, UsersView, MeView, UserView


urlpatterns = [
    path('v1/auth/signup/', SignupView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/users/', UsersView.as_view()),
    path('v1/users/me/', MeView.as_view()),
    path('v1/users/<slug:username>/', UserView.as_view()),
]
