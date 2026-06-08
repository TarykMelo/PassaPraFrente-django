import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg
from pedidos.models import Feedback

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    telefone = models.CharField(max_length=11)
    dois_fatores = models.BooleanField(default=False)
    email_verificado = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname', 'telefone']

    def __str__(self):
        return self.nickname

    @property
    def media_avaliacoes(self):
        media = Feedback.objects.filter(
            vendedor=self
        ).aggregate(
            media=Avg('nota')
        )['media']

        return round(media, 1) if media else 0
    
    @property
    def total_avaliacoes(self):
        return Feedback.objects.filter(
            vendedor=self
        ).count()
    
    def total_produtos(self):
        return self.produtos.count()
    
    def tem_produtos(self):
        return self.produtos.exists()

class CodigoVerificacao(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='codigos'
    )
    
    codigo     = models.CharField(max_length=6)
    metodo     = models.CharField(max_length=10, choices=[('email', 'Email'), ('sms', 'SMS')])
    criado_em  = models.DateTimeField(auto_now_add=True)
    usado      = models.BooleanField(default=False)

    def expirado(self):
        """
        O código expira em 10 minutos
        """
        return timezone.now() > self.criado_em + timezone.timedelta(minutes=10)
    
    @staticmethod
    def gerar_codigo():
        """
        Gera um código aleatório de 6 dígitos
        """
        return str(random.randint(100000, 999999))
    
    def __str__(self):
        return f"{self.usuario.nickname} - {self.codigo}"