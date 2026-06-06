from django.db import models
from django.conf import settings

class Notificacao(models.Model):

    TIPOS = [
        ('pedido_recebido',     '🛒 Pedido recebido'),
        ('pedido_confirmado',   '✅ Pedido confirmado'),
        ('pedido_cancelado',    '❌ Pedido cancelado'),
        ('venda_concluida',     '🎉 Venda concluída'),
        ('nova_mensagem',       '💬 Nova mensagem'),
        ('produto_editado',     '✏️ Anúncio editado'),
        ('produto_denunciado',  '❗ Produto denunciado'),
        ('produto_removido',    '🔒 Anúncio removido'),
        ('nova_avaliacao',      '⭐ Nova avaliação'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificacoes'
    )
    tipo = models.CharField(max_length=30, choices=TIPOS)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.usuario.nickname} - {self.get_tipo_display()}"