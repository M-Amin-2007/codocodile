#--------------------------------   Depemdencies   --------------------------------


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render
from users.models import MyUser
from main.models import *
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render, reverse


@csrf_exempt
def home(request):
    """  This function shows home  """
    allposts = Post.objects.all().order_by('-id')
    return render(request, 'index.html', {'posts':allposts})


@csrf_exempt
def create_post(request):
    """  This function create a post  """
    caption  = request.POST.get("caption")
    media_link  = request.POST.get("media_link")
    user  = MyUser.objects.get(username=request.user.username)
    Post.objects.create(caption=caption, media_link=media_link, user=user)
    return redirect(request, reverse("main:home"))


@csrf_exempt
def rate_post(request):
    """..."""
    id = request.POST.get("id")
    rate = request.POST.get("rate")
    mu = MyUser.objects.get(username=request.user.username)
    post = Post.objects.get(id=id)
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
