#--------------------------------   Depemdencies   --------------------------------


from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from main.models import Post, Rate



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
    

