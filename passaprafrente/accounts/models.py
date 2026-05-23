from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    telefone = models.CharField(max_length=11)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname', 'telefone']

    def __str__(self):
        return self.nickname
    
    def total_produtos(self):
        return self.produtos.count()
    
    def tem_produtos(self):
        return self.produtos.exists()