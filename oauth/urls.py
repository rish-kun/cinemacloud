from django.urls import path
from .views import *
app_name = "oauth"
urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout_view, name='logout'),
    path("profile", profile, name="profile")
]
