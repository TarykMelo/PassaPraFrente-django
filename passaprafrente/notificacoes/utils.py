from .models import Notificacao

class CriarNotificacao:

    @staticmethod
    def pedido_confirmado(pedido):
        """
        Notificação de pedido confirmado para o comprador
        """
        Notificacao.objects.create(
            usuario = pedido.comprador,
            tipo = 'pedido_confirmado',
            mensagem = f'Seu pedido de "{pedido.produto.nome}" foi confirmado pelo vendedor',
            url = f'/pedidos/meus/',
        )

    @staticmethod
    def pedido_recebido(pedido):
        """
        Vendedor recebe uma notificação de quando algum produto seu é solicitado
        """
        Notificacao.objects.create(
            usuario  = pedido.vendedor,
            tipo     = 'pedido_recebido',
            mensagem = f'🛒 {pedido.comprador.nickname} fez um pedido do seu produto "{pedido.produto.nome}"!',
            url      = f'/pedidos/vendas/'
        )

    @staticmethod
    def pedido_cancelado(pedido, usuario):
        """
        Notificação de pedido cancelado para o vendedor
        """
        Notificacao.objects.create(
            usuario = usuario,
            tipo = 'pedido_cancelado',
            mensagem = f'O pedido de "{pedido.produto.nome}" foi cancelado',
            url = f'/pedidos/meus/'
        )

    @staticmethod
    def venda_concluida(pedido):
        """
        Notificação de venda concluida, primeiro pro vendedor, e o segundo é pro comprador
        """
        Notificacao.objects.create(
            usuario = pedido.vendedor,
            tipo = 'venda_concluida',
            mensagem = f'🎉 Venda de "{pedido.produto.nome}" concluída com sucesso!',
            url = f'/pedidos/historico/vendas/',
        )
    
        Notificacao.objects.create(
            usuario = pedido.comprador,
            tipo = 'venda_concluida',
            mensagem = f'🎉 Venda de "{pedido.produto.nome}" concluída com sucesso!',
            url = f'/pedidos/historico/compras/',
        )

    @staticmethod
    def nova_mensagem(mensagem):
        """
        Notificação de mensagem nova foi recebida
        """
        pedido = mensagem.pedido
        destinatario = pedido.vendedor if mensagem.remetente == pedido.comprador else pedido.comprador

        Notificacao.objects.create(
            usuario = destinatario,
            tipo = 'nova_mensagem',
            mensagem = f'💬 Nova mensagem de {mensagem.remetente.nickname} sobre "{pedido.produto.nome}"',
            url = f'/pedidos/chat/{pedido.id}/'
        )
    
    @staticmethod
    def produto_editado(produto):
        """
        Notificação de que o produto foi editado
        """
        Notificacao.objects.create(
            usuario = produto.vendedor,
            tipo = 'produto_editado',
            mensagem = f'✏️ Seu anúncio "{produto.nome}" foi editado com sucesso.',
            url = f'/produtos/meus-produtos/'
        )

    @staticmethod
    def produto_denunciado(denuncia):
        """
        Notificação de que o produto foi denunciado
        """
        Notificacao.objects.create(
            usuario = denuncia.produto.vendedor,
            tipo = 'produto_denunciado',
            mensagem = f'👀 Seu produto "{denuncia.produto.nome}" recebeu uma denúncia.',
            url = f'/produtos/meus-produtos/',
        )

    @staticmethod
    def nova_avaliacao(feedback):
        Notificacao.objects.create(
            usuario = feedback.vendedor,
            tipo = 'nova_avaliacao',
            mensagem = f'⭐ {feedback.avaliador.nickname} avaliou você com nota {feedback.nota}.',
            url = f'/conta/vendedor/{feedback.vendedor.id}/'
        )