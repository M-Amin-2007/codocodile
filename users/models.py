"""define models to create database from those by django."""
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# Create your models here.

class MyUser(User):
    score = models.FloatField(default=3, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    active = models.BooleanField(default=False)


class ActivationCodes(models.Model):
    """a model of database for activation linkes that send by email."""
    username = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
