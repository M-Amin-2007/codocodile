"""manage urls send to this app"""
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("post/create/", views.create_post, name="user"),
    path("signout/", views.signout, name="signout"),
    path("change_pass/", views.change_password, name="change_password"),
    path("change_username/", views.change_username, name="change_username"),
    path("change_email/", views.change_email, name="change_email"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
]