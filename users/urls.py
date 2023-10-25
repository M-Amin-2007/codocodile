"""manage urls send to this app"""
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("change_pass/", views.change_password, name="change_password"),
    path("change_username/", views.change_username, name="change_username"),
    path("change_email/", views.change_email, name="change_email"),
    path("logout/", views.logout_view, name="logout_view"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login_view"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path("user/", views.user, name="user"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("send/", views.send_gmail)
]