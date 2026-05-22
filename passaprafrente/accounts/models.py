from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    telefone = models.CharField(max_length=11)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname', 'telefone']
    