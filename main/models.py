from django.db import models
from users import models as usermodel


class Post(models.Model):
    caption = models.TextField()
    image = models.ImageField(null=True, blank=True)
    user = models.ForeignKey(usermodel.MyUser, on_delete=models.CASCADE)
    nor = models.FloatField(default=0)  # number of rates
    avg_rate = models.FloatField(default=0)


class Rate(models.Model):
    rate = models.FloatField()
    user = models.ForeignKey(usermodel.MyUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
