from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from produtos.models import Produto
from .models import Pedido

@login_required
def fazer_pedido(request, produto_id):
    """
    Função de fazer_pedido com as restrições de não poder pedido duplicado ou se o produto é do próprio usuário
    """
    produto = get_object_or_404(Produto, id=produto_id)

    if produto.vendedor == request.user:
        return redirect('user_menu')
    
    ja_pedido = Pedido.objects.filter(
        produto=produto,
        comprador=request.user
    ).exists()

    if ja_pedido:
        return redirect('user_menu')
    
    if request.method == 'POST':
        Pedido.objects.create(produto=produto, comprador=request.user)

    return render(request, 'pedidos/confirmar_pedido.html', {'produto': produto})

@login_required
def meus_pedidos(request):
    """
    Função para a página de ver meus pedidos
    """
    pedidos = Pedido.objects.filter(
        comprador=request.user
    ).selec_related('produto', 'produto__vendedor')
    return render(request, 'pedidos/meus_pedidos.html', {'pedidos': pedidos})

@login_required

def cancelar_pedido(request, pedido_id):
    """
    Função para deletar o pedido feito pelo usuário 
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
    if request.method == 'POST':
        pedido.delete()
    return redirect('meus_pedidos')