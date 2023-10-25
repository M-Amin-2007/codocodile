"""manage account views."""
import datetime
import json
import os
import pathlib
import pytz
import random
import re
import ssl
import smtplib
import string
from email.message import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from codocodile.settings import BASE_DIR
from users.models import *

now = datetime.datetime.now
LINK_TIME = 30
def random_str(num):
    random_string = str()
    accepted_char = string.ascii_letters + string.digits + "@#$!^"
    for _ in range(num):
        random_string += random.choice(accepted_char)
    return random_string
    

@csrf_exempt
def register(request):
    """register user."""

    if request.user.is_authenticated and not request.user.is_superuser:
        # befor this signed in
        return redirect(reverse("users:user"))   
    elif request.POST:
        # proccess form data and send email
        username = request.POST["username"]
        prefix = "https://" if request.is_secure() else "http://"
        code = random_str(random.randint(20, 30))
        body = f"""
        {prefix}{request.get_host()}/user/register?username={username}&code={code}
        """
        send_gmail(body, request.POST["email"], "Rategram")
        ActivationCodes.objects.create(username=username, code=code)
        new_user = MyUser.objects.create_user(username=request.POST["username"], password=request.POST["password"],
                                        email=request.POST["email"])
        return JsonResponse({"status":"email send"})
    elif "code" in request.GET:
        # accommadating activation link
        username = request.GET["username"]
        code = request.GET["code"]
        activation_code = ActivationCodes.objects.filter(username=username, code=code)
        if activation_code:
            a_code = activation_code[0]
            a_code.delete()
            this_user = User.objects.get(username=username)
            this_user.active = True
            this_user.save()
            login(request, this_user)
            return JsonResponse({"status": "activated"})
        return JsonResponse({"status": "invalid activation link"})
    else:
        # show form
        print(request.GET)
        context = {"message": ""}
        return JsonResponse(context)


@csrf_exempt
def user(request):
    """user panel view."""
    if request.user.is_authenticated and not request.user.is_superuser:
        return JsonResponse({"user_name":request.user.username})
    else:
        return JsonResponse({"status": "user not authenticated!!"})
        # return redirect(reverse("users:login"))


@csrf_exempt
def login_view(request):
    """login page view."""
    if request.user.is_authenticated and not request.user.is_superuser:
        return JsonResponse({"a":'redirect(reverse("users:user"))'})
        # return redirect(reverse("users:user"))
    elif "username" in request.POST:
        username = request.POST.get("username")
        print(username)
        password = request.POST.get("password")
        if not MyUser.objects.filter(username=username) or MyUser.objects.get(username=username).is_superuser:
            context = {"message": "this username isn't exist."}
            return JsonResponse(context)
        else:
            this_user = authenticate(username=username, password=password)
            if this_user:
                login(request, this_user)
                return JsonResponse({"a": 'redirect(reverse("users:user"))', "b": "login"})
                # return redirect(reverse("users:user"))
            else:
                context = {"message": "password is incorrect."}
                return JsonResponse(context)
    else:
        context = {"message": ""}
        return JsonResponse(context)


@csrf_exempt
def change_password(request):
    """change password"""
    if request.method == "GET":
        raise Http404("not found!")
    elif request.user.is_authenticated and not request.user.is_superuser:
        if "pass1" in request.POST:
            pass1 = request.POST.get("pass1")
            new_pass = request.POST.get("pass2")
            this_user = request.user
            if authenticate(username=this_user.username, password=pass1) != this_user:
                context = {"message": "the old password is incorrect!"}
                return JsonResponse(context)
            else:
                this_user.set_password(new_pass)
                this_user.save()
                login(request, this_user)
                return JsonResponse({"message":"the password changed"})
        else:
            context = {"message": ""}
            return render(request, "users/change_password.html", context=context)
    else:
        return redirect(reverse("users:login"))

    """
    prefix = "https://" if request.is_secure() else "http://"
    body = f\"\"\"
    please click link to activate your account:
    {prefix}{request.get_host()}/account/forgot_password/
    this activating code is valid for {30} minutes
    \"\"\"
    """
def send_gmail(body, reciever, subject):
    """frg"""
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
        server.sendmail(sender, em["To"], em.as_string())
    return JsonResponse({"status": "OK"})
    

@csrf_exempt
def change_username(request):
    """change password"""
    if request.method == "GET":
        raise Http404("not found!")
    elif request.user.is_authenticated and not request.user.is_superuser:
        if "new_username" in request.POST:
            new_username = request.POST.get("new_username")
            this_user = request.user
            if MyUser.objects.filter(username=new_username).exists():
                context = {"message": "this username exists. you can't use it."}
                return render(request, "users/change_username.html", context=context)
            else:
                this_user.username = new_username
                this_user.save()
                login(request, this_user)
                return redirect(reverse("users:user"))
        else:
            context = {"message": ""}
            return render(request, "users/change_username.html", context=context)
    else:
        return redirect(reverse("users:login"))


@csrf_exempt
def change_email(request):
    """change password"""
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.method == "GET":
            if "code" in request.GET:
                code = request.GET.get("code")
                email = request.GET.get("email").lower()
                code_temp = AccountActivatingCodes.objects.get(code=code)
                this_user = request.user
                if not code_temp.user_name == this_user.username:
                    context = {"message": "this activating code is not valid for this user."}
                    return render(request, "users/change_email.html", context=context)
                else:
                    this_user.email = email
                    this_user.save()
                    login(request, this_user)
                    return redirect(reverse("users:user"))
            else:
                raise Http404("not found!")

        if "new_email" in request.POST:
            new_email = request.POST.get("new_email").lower()
            this_user = request.user
            if MyUser.objects.filter(username=new_email).exists():
                context = {"message": "this email was used before this."}
                return render(request, "users/change_email.html", context=context)
            else:
                code = random_str(30)
                secret_file = pathlib.Path(
                    os.path.join(BASE_DIR, f"users/static/users/secret.json"))
                sender_info = json.loads(secret_file.read_text())
                sender = sender_info.get("sender_email")
                sender_password = sender_info.get("password")
                prefix = "https://" if request.is_secure() else "http://"
                body = f"""
                click on this link to change your email to this email:
                {prefix}{request.get_host()}/account/change_email/?email={new_email}&code={code}
                """
                message = EmailMessage()
                message["Subject"] = "Bestoon"
                message["From"] = sender
                message["To"] = new_email
                message.set_content(body)
                with smtplib.SMTP("smtp.gmail.com", 465) as server:
                    server.login(sender, sender_password)
                    server.sendmail(sender, new_email, message.as_string())
                AccountActivatingCodes.objects.create(code=code, user_name=this_user.username, password="",
                                                      date=now(), email=new_email)
                return render(request, "users/email_send.html")
        else:
            context = {"message": ""}
            return render(request, "users/change_email.html", context=context)
    else:
        return redirect(reverse("users:login"))


@csrf_exempt
def logout_view(request):
    """log out user"""
    logout(request)
    return JsonResponse({"a": "hallleeeee!"})
    # return redirect(reverse("users:user"))


@csrf_exempt
def delete_account(request):
    """delete_account"""
    if request.method == "GET":
        raise Http404("not found!")
    else:
        user = request.user
        user.delete()
        return redirect(reverse("users:login"))


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
        else:
            this_user.set_password(new_pass)
            this_user.save()
            login(request, this_user)
            return redirect(reverse("users:user"))
    elif "username" in request.POST:
        username = request.POST.get("username").lower().title()
        email = request.POST.get("email").lower()
        try:
            this_user = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            context = {"message": "username not found!"}
            return render(request, "users/forgot_password.html", context=context)
        else:
            if re.sub(r"\s\w+@", "@", this_user.email) == email:
                code = random_str(28)
                # send mail
                secret_file = pathlib.Path(
                    os.path.join(BASE_DIR, f"users/static/users/secret.json"))
                sender_info = json.loads(secret_file.read_text())
                sender = sender_info.get("sender_email")
                sender_password = sender_info.get("password")
                prefix = "https://" if request.is_secure() else "http://"
                body = f"""
                please click link to activate your account:
                {prefix}{request.get_host()}/account/forgot_password/?email={email}&code={code}&username={username}
                this activating code is valid for {FORGOT_LINK_TIME} minutes
                """
                em = EmailMessage()
                em["From"] = sender
                em["To"] = email
                em["Subject"] = "Bestoon forgot password"
                em.set_content(body)
                with smtplib.SMTP("smtp.gmail.com", 465) as server:
                    server.login(sender, sender_password)
                    server.sendmail(sender, email, em.as_string())
                AccountActivatingCodes.objects.create(email=email, date=now(), code=code, user_name=username,
                                                      password="")
                return render(request, "users/email_send.html")
            else:
                context = {"message": "this email isn't for this user."}
                return render(request, "users/forgot_password.html", context=context)
    elif "code" in request.GET.keys():
        username = request.GET.get("username")
        email = request.GET.get("email")
        code = request.GET.get("code")
        try:
            temp_code = AccountActivatingCodes.objects.get(user_name=username, code=code, email=email)
        except AccountActivatingCodes.DoesNotExist:
            context = {"message": "forgot password code is not valid. create new one with this form!"}
            return render(request, "users/forgot_password.html", context=context)
        else:
            time_difference = pytz.utc.localize(now()) - temp_code.date
            if time_difference.seconds > FORGOT_LINK_TIME * 60:
                context = {"message": "forgot password code time is over. create new one with this form!"}
                return render(request, "users/forgot_password.html", context=context)
            else:
                this_user = MyUser.objects.get(username=username)
                login(request, this_user)
                context = {"change_password": True}
                return render(request, "users/forgot_password.html", context=context)
        return redirect(reverse("web:home"))
    else:
        return render(request, "users/forgot_password.html")
