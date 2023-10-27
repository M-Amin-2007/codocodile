#--------------------------------   Depemdencies   --------------------------------


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render
from users.models import MyUser
from main.models import *



#--------------------------------   Variables   --------------------------------





#--------------------------------   Functions   --------------------------------



    

#--------------------------------   APIs   --------------------------------


@csrf_exempt
def home(request):
    """  This function shows home  """
    
    return render(request, "index.html")


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
    return JsonResponse({"post_id": id, "new_post_rate": post.avg_rate})

@csrf_exempt
def del_post(request):
    """delete post"""
    post_id = request.POST.get("post_id")
    post = Post.objects.get(id=post_id)
    user_posts = Post.objects.filter(user=post.user)
    post.user.score = (post.user.score * len(user_posts) - post.avg_rate) / (len(user_posts) - 1)
    post.user.save()
    post.delete()
    return JsonResponse({"message": "post deleted"})     

@csrf_exempt
def user_posts(request):
    """posts of spiecific user"""
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
