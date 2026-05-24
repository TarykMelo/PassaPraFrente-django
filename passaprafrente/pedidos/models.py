from django.db import models
from django.conf import settings
from produtos.models import Produto

class Pedido(models.Model):
    """
    Classe pedidos que possui as informações do comprador e com restrição de só ser possível pedir o mesmo produto uma vez
    """
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('produto', 'comprador')

    def __str__(self):
        return f"{self.comprador.nickname} -> {self.produto.nome}"
    