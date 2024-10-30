from django.urls import path
from .views import *
app_name = "main"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login", LoginView.as_view(), name="login"),
    path("signup", SignupView.as_view(), name="signup"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("movie/<str:movie_id>", MovieView.as_view(), name="movie"),
]
