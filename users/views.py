#--------------------------------   Depemdencies   --------------------------------


import os
import re
import random
import datetime
import json
import pathlib
import pytz
import ssl
import smtplib
import string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from email.message import EmailMessage
from codocodile.settings import BASE_DIR
from users.models import *


#--------------------------------   Variables   --------------------------------


now = datetime.datetime.now


#--------------------------------   Functions   --------------------------------


def random_str(num):
    """ This function returns a random string """
    
    random_string = str()
    accepted_char = string.ascii_letters + string.digits
    for _ in range(num):
        random_string += random.choice(accepted_char)
    return random_string


def send_gmail(body, reciever, subject):
    """This function send email for activating account and changing email & password """
    
    secret_file = pathlib.Path(
            os.path.join(BASE_DIR, f"users/static/users/secret.json"))
    sender_info = json.loads(secret_file.read_text())
    sender = sender_info.get("sender_email")
    sender_password = sender_info.get("password")
    em = EmailMessage()
    em["From"] = sender
    em["To"] = reciever
    em["Subject"] = subject
    em.set_content(body)
    ssl_context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl_context) as server:
        server.login(sender, sender_password)
        try:
            server.sendmail(sender, reciever, em.as_string())
        except smtplib.SMTPRecipientsRefused:
            return JsonResponse({"message": "invalid email"})
    return JsonResponse({"message": "OK"})
    

#--------------------------------   APIs   --------------------------------


@csrf_exempt
def user(request):
    """ This API returns user information """
    
    if request.user.is_authenticated and not request.user.is_superuser:
        this_user = MyUser.objects.get(username=request.user.username)
        return JsonResponse({"username": this_user.username,
                             "email": this_user.email,
                             "score": this_user.score})
    else:
        return JsonResponse({"message": "user not authenticated !!"})


@csrf_exempt
def signin(request):
    """ This function signs in tje user """
    
    if request.user.is_authenticated and not request.user.is_superuser:
        return JsonResponse({"message": "user was logged in !!"})
    username = request.POST.get("username")
    password = request.POST.get("password")
    if not MyUser.objects.filter(username=username) or MyUser.objects.get(username=username).is_superuser:
        return JsonResponse({"message": "this username isn't exist !!"})

    this_user = authenticate(username=username, password=password)
    if this_user:
        login(request, this_user)
        return JsonResponse({"message": "user logged in !!"})
    context = {"message": "password is incorrect !!"}
    return JsonResponse(context) 


@csrf_exempt
def signup(request):
    """ This function register a new user """
    print(request.method)
    if request.user.is_authenticated and not request.user.is_superuser:
        return JsonResponse({"message": "user was logged in !!"}) 
    elif request.method == "POST":
        username = request.POST.get("username")
        print("----------------------------------------")
        print(request.POST)
        print(username)
        print("----------------------------------salam", request.POST.get("email"))
        if not MyUser.objects.filter(username=username):
            prefix = "https://" if request.is_secure() else "http://"
            code = random_str(random.randint(20, 30))
            body = f"""
            {prefix}{request.get_host()}/user/signup?username={username}&code={code}
            """
            print("-------***---------------------------salam", request.POST.get("email"))
            res = send_gmail(body, request.POST.get("email"), "Rategram SignUp")
            ActivationCodes.objects.create(username=username, code=code)
            MyUser.objects.create_user(username=username, password=request.POST.get("password"),
                                        email=request.POST.get("email"))
            return JsonResponse(res)
        return JsonResponse({"message":"username exists !!"})
    elif "code" in request.GET:
        username = request.GET.get("username")
        code = request.GET.get("code")
        activation_code = ActivationCodes.objects.filter(username=username, code=code)
        print(activation_code)
        if activation_code:
            activation_code[0].delete()
            this_user = MyUser.objects.get(username=username)
            this_user.email_active = True
            this_user.save()
            login(request, this_user)
            return JsonResponse({"message": "account activated !!"})
        return JsonResponse({"message": "invalid or expired activation link !!"})
    else:
        # show form
        # need to complete
        context = {"message": ""}
        return JsonResponse(context)


@csrf_exempt
def signout(request):
    """ This function signs out user """
    if request.user.is_authenticated and not request.user.is_superuser:
        logout(request)
        return JsonResponse({"message": "user succesfully signed out !!"})
    return JsonResponse({"message": "user not authenticated !!"})


@csrf_exempt
def change_password(request):
    """ This function changes the user's password. this function is diferent from forgot password """
    if request.user.is_authenticated and not request.user.is_superuser:
        pass1 = request.POST.get("pass1")
        new_pass = request.POST.get("pass2")
        this_user = request.user
        if authenticate(username=this_user.username, password=pass1) == this_user:
            this_user.set_password(new_pass)
            this_user.save()
            login(request, this_user)
            return JsonResponse({"message":"the password succesfully changed !!"})
        else:
            return JsonResponse({"message": "the old password is incorrect !!"})
    else:
        return JsonResponse({"message": "user not authenticated !!"})


@csrf_exempt
def change_username(request):
    """ This function changes the user's username """
    
    if request.user.is_authenticated and not request.user.is_superuser:
        new_username = request.POST.get("new_username")
        this_user = request.user
        if MyUser.objects.filter(username=new_username).exists():
            return JsonResponse({"message": "this username exists !!"})
        this_user.username = new_username
        this_user.save()
        login(request, this_user)
        return JsonResponse({"message": "username succesfully changed !!"})
    else:
        return JsonResponse({"message": "user not authenticated !!"})


@csrf_exempt
def change_email(request):
    """ This function changes user's email """
    
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.method == "GET":
            if "code" in request.GET:
                code = request.GET.get("code")
                email = request.GET.get("email").lower()
                code_temp = ActivationCodes.objects.get(code=code)
                this_user = request.user
                if code_temp.username == this_user.username:
                    this_user.email = email
                    this_user.save()
                    login(request, this_user)
                    return JsonResponse({"message": "email succesfully chanaged !!"})
                return JsonResponse({"message": "invalid or expired activation link !!"})
            return JsonResponse({"message": "invalid activation link !!"})
        new_email = request.POST.get("new_email").lower()
        this_user = request.user
        if MyUser.objects.filter(email=new_email).exists():
            return JsonResponse({"message": "this email was used before this !!"})
        code = random_str(random.randint(20, 30))
        prefix = "https://" if request.is_secure() else "http://"
        body = f"""
        click on this link to change your email to this email:
        {prefix}{request.get_host()}/user/change_email/?email={new_email}&code={code}
        """
        send_gmail(body, new_email, "Rategram ChangeEmail")
        ActivationCodes.objects.create(code=code, username=this_user.username)
        return JsonResponse({"message": "an email sent to the new email !!"})
    return JsonResponse({"message": "user not authenticated !!"})


@csrf_exempt
def delete_account(request):
    """ This function deletes teh user's account """
    if request.user.is_authenticated and not request.user.is_superuser:
        mu = MyUser.objects.get(username=request.user.username)
        mu.delete()
        return JsonResponse({"message": "account succesfully deleted !!"})
    return JsonResponse({"message": "user not authenticated !!"})


@csrf_exempt
def forgot_password(request):
    """forgot pass word view"""
    
    if "pass1" in request.POST.keys():
        this_user = request.user
        new_pass_repeat = request.POST.get("pass2")
        new_pass = request.POST.get("pass1")
        if new_pass != new_pass_repeat:
            context = {"message": "your repeat field isn't correct!"}
            return JsonResponse(context)
        this_user.set_password(new_pass)
        this_user.save()
        login(request, this_user)
        return JsonResponse({"message": "old password succesfully changed"})
    elif "username" in request.POST:
        username = request.POST.get("username")
        email = request.POST.get("email").lower()
        try:
            this_user = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            return JsonResponse({"message": "this username isn't exist !!"})
        if re.sub(r"\s\w+@", "@", this_user.email) == email:
            code = random_str(random.randint(20,30))
            prefix = "https://" if request.is_secure() else "http://"
            body = f"""
            please click link to activate your account:
            {prefix}{request.get_host()}/user/forgot_password/?username={usename}&code={code}&email={email}
            """
            send_gmail(body, email, "Rategram ForgotPassword")
            ActivationCodes.objects.create(code=code, username=username)
            return JsonResponse({"message": "forgot password email sent !!"})
        return JsonResponse({"message": "this email isn't for this user !!"})
    elif "code" in request.GET.keys():
        username = request.GET.get("username")
        code = request.GET.get("code")
        
        try:
            ActivationCodes.objects.get(code=code)
        except ActivationCodes.DoesNotExist:
            return JsonResponse({"message": "forgot password link is not valid or expired !!"})
        this_user = MyUser.objects.get(username=username)
        login(request, this_user)
        context = {"change_password": True}
        return JsonResponse({"message": "load change password form."})
    return JsonResponse({"message": "form"})
