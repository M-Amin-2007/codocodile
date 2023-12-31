from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


class MyUser(User):
    score = models.FloatField(default=3, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    email_active = models.BooleanField(default=False)


class ActivationCodes(models.Model):
    """A model of database for activation linkes that send by email."""
    username = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
