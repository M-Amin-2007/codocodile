"""manage urls send to this app"""
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("post/create/", views.create_post, name="create_post"),
    path("post/rate/", views.rate_post, name="rate_post"),
]