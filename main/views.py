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


@api_view(['POST'])
@csrf_exempt
def create_post(request):
    """  This function create a post  """
    caption  = request.POST.get("caption")
    media_link  = request.POST.get("media_link")
    user  = request.user
    Post.objects.create(caption=caption, media_link=media_link, user=user)
    return JsonResponse({"message": "Post succesfully created"})


@api_view(['POST'])
@csrf_exempt
def post_info(request):
    """ This function returns the post information """
    post_id = request.POST.get("id")
    

@api_view(['POST'])
@csrf_exempt
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
