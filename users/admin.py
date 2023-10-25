from django.contrib import admin
from users.views import *

# Register your models here.
admin.site.register(MyUser)
admin.site.register(ActivationCodes)