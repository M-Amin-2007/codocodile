#--------------------------------   Depemdencies   --------------------------------


from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from users.models import MyUser
from main.models import *



#--------------------------------   Variables   --------------------------------





#--------------------------------   Functions   --------------------------------



    

#--------------------------------   APIs   --------------------------------

def rate_post(request):
    """..."""
    rate = request.POST.get("rate")
    post = request.POST.get("post")
    mu = MyUser.objects.get(username=request.user.username)
    Rate.objects.create(rate=rate, user=mu, post=post)
    post.nor += 1
    post.avg_rate = (post.avg_rate + rate) / post.nor
    post.save()
    return JsonResponse({"post": post, "new_rate": post.avg_rate})
