from django.urls import path

from .views_auth import LoginView, LogoutView

# OJO: sin "/" al final porque Angular llama a /api/auth/login (ver auth.service.ts)
urlpatterns = [
    path("login", LoginView.as_view()),
    path("logout", LogoutView.as_view()),
]
