from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", views.login, name="login"),
    path("admin/", views.admin, name="admin"),
    path("medico/", views.medico, name="medico"),
    path("secretaria/", views.secretaria, name="secretaria"),
    path("logout/", views.logout, name="logout"),
]