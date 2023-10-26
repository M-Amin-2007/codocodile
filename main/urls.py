"""manage urls send to this app"""
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("post/create/", views.create_post, name="create_post"),
    path("post/info/", views.post_info, name="post_info"),
]
