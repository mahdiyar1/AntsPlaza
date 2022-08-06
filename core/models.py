from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=255, unique=True)
