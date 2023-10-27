""" Manage urls send to this app """
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("emailsent/", views.email_sent, name="email_sent"),                                 
    path("user/", views.user, name="user"),                                 
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("signout/", views.signout, name="signout"),
    path("change_pass/", views.change_password, name="change_password"),
    path("change_username/", views.change_username, name="change_username"),
    path("change_email/", views.change_email, name="change_email"),
    path("delete_account/", views.delete_account, name="delete_account"),
]