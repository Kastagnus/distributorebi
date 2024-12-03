from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=200,)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    ltd_name = models.CharField(max_length=100, blank=True, null=True)
    identification_number = models.IntegerField(blank=True, null=True, unique=True,)
    phone_number = models.IntegerField(blank=True, null=True)
    brand_name = models.CharField(max_length=100, blank=True, null=True)
    is_seller = models.BooleanField(default=False)




# Create your models here.
