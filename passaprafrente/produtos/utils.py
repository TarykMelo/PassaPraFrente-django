from pedidos.models import Pedido
from .models import Produto

class ProdutosDisponiveis:

    @staticmethod
    def get(usuario, categoria=None):
        """
        Retorna produtos disponíveis para um usuário específico
        """

        todos_pedidos_ativos = Pedido.objects.filter(
            status__in=['pendente', 'compra_confirmada', 'aguardando_confirmacao', 'finalizado']
        ).values_list('produto_id', flat=True)

        pedidos_cancelados_do_usuario = Pedido.objects.filter(
            comprador=usuario,
            status__in=['cancelamento_solicitado', 'cancelado']
        ).values_list('produto_id', flat=True)

        produtos = Produto.objects.exclude(
            vendedor=usuario
        ).exclude(
            id__in=todos_pedidos_ativos
        ).exclude(
            id__in=pedidos_cancelados_do_usuario
        ).filter(vendido=False)

        if categoria:
            produtos = produtos.filter(categoria=categoria)

        return produtos