"""manage urls send to this app"""
from django.urls import path
from . import views


app_name = "main"

urlpatterns = [
    path("post", views.home, name="home"),
    path("post/create/", views.create_post, name="create_post"),
    path("post/rate/", views.rate_post, name="rate_post"),
    path("post/info/", views.post_info, name="post_info"),
    path("post/del/", views.del_post, name="del_post"),
    path("post/user/", views.user_posts, name="user_posts"),
]
