from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from produtos.models import Produto
from .models import Pedido


class FazerPedidoView(LoginRequiredMixin, View):
    """
    View de fazer pedido com restrições de pedido duplicado
    e produto do próprio usuário
    """
    def get(self, request, produto_id):
        produto = get_object_or_404(Produto, id=produto_id)

        if produto.vendedor == request.user:
            return redirect('user_menu')

        ja_pedido = Pedido.objects.filter(
            produto=produto,
            comprador=request.user
        ).exists()

        if ja_pedido:
            return redirect('user_menu')

        return render(request, 'pedidos/confirmar_pedido.html', {'produto': produto})

    def post(self, request, produto_id):
        produto = get_object_or_404(Produto, id=produto_id)

        if produto.vendedor == request.user:
            return redirect('user_menu')

        ja_pedido = Pedido.objects.filter(
            produto=produto,
            comprador=request.user
        ).exists()

        if ja_pedido:
            return redirect('user_menu')

        Pedido.objects.create(produto=produto, comprador=request.user)
        return redirect('user_menu')


class MeusPedidosView(LoginRequiredMixin, View):
    """
    View para a página de ver meus pedidos
    """
    def get(self, request):
        pedidos = Pedido.objects.filter(
            comprador=request.user
        ).select_related('produto', 'produto__vendedor')
        return render(request, 'pedidos/meus_pedidos.html', {'pedidos': pedidos})


class CancelarPedidoView(LoginRequiredMixin, View):
    """
    View para deletar o pedido feito pelo usuário
    """
    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
        pedido.delete()
        return redirect('meus_pedidos')