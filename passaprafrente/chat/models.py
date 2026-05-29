from django.db import models
from django.conf import settings
from pedidos.models import Pedido

# Create your models here.

class Mensagem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensagens_enviadas'
    )
    conteudo = models.TextField()
    enviado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['enviado_em']

    def __str__(self):
        return f"{self.remetene.nickname}: {self.conteudo[:30]}"
    
