#--------------------------------   Depemdencies   --------------------------------


from django.views.decorators.csrf import csrf_exempt
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
    post_data = json.loads(request.body.decode("utf-8"))
    caption  = post_data.get("caption")
    media_link  = post_data.get("media_link")
    user  = MyUser.objects.get(username=post_data.get("username"))
    Post.objects.create(caption=caption, media_link=media_link, user=user)
    return JsonResponse({"message": "Post succesfully created"})

@csrf_exempt
def post_info(request):
    """ This function returns the post information """
    post_data = json.loads(request.body.decode("utf-8"))
    post_range = post_data.get("post")
    mu = MyUser.objects.get(username=post_data.get("username"))
    no_all = Post.objects.all().count()
    context_list = list()
    for id in range(post_range[0], post_range[1] + 1):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            continue
        if post.user is mu:
            user_rate = post.avg_rate
        else:
            try:
                user_rate = Rate.objects.get(post=post, user=mu).rate
            except Rate.DoesNotExist:
                user_rate = 0
        context = {"id":id,
                "caption": post.caption,
                "media_link": post.media_link,
                "username": post.user.username,
                "email": post.user.email,
                "nor": post.nor,
                "avg_rate": round(post.avg_rate, 2),
                "user_rate": user_rate}
        context_list.append(context)
    return JsonResponse({"context": json.dumps(context_list), "length": len(context_list)})

@csrf_exempt
def rate_post(request):
    """..."""
    post_data = json.loads(request.body.decode("utf-8"))
    id = post_data.get("id")
    rate = post_data.get("rate")
    mu = MyUser.objects.get(username=post_data.get("username"))
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return JsonResponse({"message": "post doesn't exist"})
    rates = Rate.objects.filter(user=mu, post=post)
    old_rate = post.avg_rate
    if mu == post.user:
        return JsonResponse({"message": "you can't rate yourself"})
    if rates:
        old_rate = rates[0].rate
        post.avg_rate = (post.avg_rate * post.nor - float(old_rate) + float(rate)) / (post.nor)
        post.save()
        rates[0].rate = rate
        rates[0].save()
    else:
        Rate.objects.create(rate=rate, user=mu, post=post)
        post.avg_rate = (post.avg_rate * post.nor + float(rate)) / (post.nor + 1)
        post.nor += 1
        post.save()
    no_posts = len(Post.objects.filter(user=post.user))
    post.user.score = (post.user.score * no_posts - old_rate + post.avg_rate) / no_posts
    post.user.save()
    return JsonResponse({"post_id": id, "new_post_rate": round(post.avg_rate, 2)})

@csrf_exempt
def del_post(request):
    """delete post"""
    post_data = json.loads(request.body.decode("utf-8"))
    post_id = post_data.get("post_id")
    post = Post.objects.get(id=post_id)
    user_posts = Post.objects.filter(user=post.user)
    post.user.score = (post.user.score * len(user_posts) - post.avg_rate) / (len(user_posts) - 1)
    post.user.save()
    post.delete()
    return JsonResponse({"message": "post deleted"})     

@csrf_exempt
def user_posts(request):
    """posts of spiecific user"""
    post_data = json.loads(request.body.decode("utf-8"))
    username = post_data.get("username")
    try:
        mu = MyUser.objects.get(username=username)
    except MyUser.DoesNotExist:
        return JsonResponse({"message": "user not exist !!"})
    posts = Post.objects.filter(user=mu)
    context_list = list()
    for post in posts:
        context = {
                "id":post.id,
                "caption": post.caption,
                "media_link": post.media_link,
                "username": post.user.username,
                "email": post.user.email,
                "avg_rate": round(post.avg_rate, 2),
        }
        context_list.append(context)
    return JsonResponse({"context_list": json.dumps(context_list),
                            "user_info": 
                                {"username": mu.username,
                            "email": mu.email,
                            "score": round(mu.score, 4)}})
