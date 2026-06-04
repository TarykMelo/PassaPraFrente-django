from django.db import models
from django.conf import settings
from produtos.models import Produto

class Pedido(models.Model):
    """
    Classe pedidos que possui as informações do comprador,vendedor, status do fluxo 
    e com restrição de só ser possível pedir o mesmo produto uma vez
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('compra_confirmada', 'Confirmada pelo vendedor'),
        ('aguardando_confirmacao', 'Aguardando confirmação do comprador'),
        ('finalizado', 'Finalizado (Venda Confirmada)'),
        ('cancelamento_solicitado', 'Cancelamento Solicitado pelo Comprador'), 
        ('cancelado', 'Cancelado'),
    ]


    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    
    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='compras'
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendas'  
    )  

    status = models.CharField(
        max_length=30, 
        choices=STATUS_CHOICES, 
        default='pendente'       
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('produto', 'comprador')

    def __str__(self):
        return f"{self.comprador.nickname} -> {self.produto.nome}"
    
    def finalizar(self):
        """Marca o pediddo como vendido quando ambos confirmaram"""
        self.status = 'finalizado'
        self.produto.vendido = True
        self.produto.save()
        self.save()
    


class Feedback(models.Model):

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='feedback_pedido', null=True, blank=True)
    
   
    avaliador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks_dados')
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks_recebidos', null=True, blank=True)
    
    nota = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Estrelas de 1 a 5
    comentario = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota {self.nota} para {self.vendedor.nickname if self.vendedor else 'Vendedor'}"

class Mensagem(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='mensagens'
    )
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
        return f"{self.remetente.nickname}: {self.conteudo[:30]}"