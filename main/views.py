#--------------------------------   Depemdencies   --------------------------------


from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from users.models import MyUser
from main.models import *
import json



#--------------------------------   Variables   --------------------------------





#--------------------------------   Functions   --------------------------------



    

#--------------------------------   APIs   --------------------------------


@csrf_exempt
def create_post(request):
    """  This function create a post  """
    caption  = request.POST.get("caption")
    media_link  = request.POST.get("media_link")
    user  = MyUser.objects.get(username=request.user.username)
    Post.objects.create(caption=caption, media_link=media_link, user=user)
    return JsonResponse({"message": "Post succesfully created"})


@csrf_exempt
def post_info(request):
    """ This function returns the post information """
    post_range = json.loads(request.POST.get("post"))
    no_all = Post.objects.all().count()
    context_list = list()
    for id in range(no_all - post_range[1] + 1, no_all - post_range[0] + 2):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            continue
        mu = MyUser.objects.get(username=request.user.username)
        if post.user is mu:
            user_rate = post.avg_rate
        else:
            try:
                user_rate = Rate.objects.get(post=post).rate
            except Rate.DoesNotExist:
                user_rate = 0
        context = {"id":id,
                "caption": post.caption,
                "media_link": post.media_link,
                "username": post.user.username,
                "email": post.user.email,
                "avg_rate": post.avg_rate,
                "user_rate": user_rate}
        context_list.append(context)
    return JsonResponse({"context": json.dumps(context_list), "length": len(context_list)})
    

@csrf_exempt
def rate_post(request):
    """..."""
    id = request.POST.get("id")
    rate = request.POST.get("rate")
    mu = MyUser.objects.get(username=request.user.username)
    post = Post.objects.get(id=id)
    rates = Rate.objects.filter(user=mu, post=post)
    if rates:
        old_rate = rates[0].rate
        print(old_rate, post.nor, post.avg_rate)
        post.avg_rate = (post.avg_rate * post.nor - float(old_rate) + float(rate)) / (post.nor)
        print(post.avg_rate)
        post.save()
        rates[0].rate = rate
        rates[0].save()
    else:
        Rate.objects.create(rate=rate, user=mu, post=post)
        post.avg_rate = (post.avg_rate * post.nor + float(rate)) / (post.nor + 1)
        post.nor += 1
        post.save()
    return JsonResponse({"post_id": id, "new_post_rate": post.avg_rate})

@csrf_exempt
def del_post(request):
    post_id = request.POST.get("post_id")
    Post.objects.get(id=post_id).delete()
    return JsonResponse({"message": "post deleted"})     

@csrf_exempt
def user_posts(request):
    username = request.POST.get("username")
    try:
        mu = MyUser.objects.get(username=username)
    except MyUser.DoesNotExist:
        return JsonResponse({"message": "user not exist !!"})
    posts = Post.objects.filter(user=mu)
    context_list = list()
    for post in posts:
        context = {
            "caption": post.caption,
            "media": post.media_link,
            "avg_rate": post.avg_rate
        }
        context_list.append(context)
    return JsonResponse({"context_list": json.dumps(context_list)})
