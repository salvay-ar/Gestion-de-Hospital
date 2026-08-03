from django.contrib import admin
from django.urls import path
from App import views

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("App.urls")),
]