from django.contrib import admin
from django.urls import path
from App import views

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("App.urls")),
]