from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from produtos.models import Produto
from .forms import ProdutoForm

@login_required
def lista_produtos(request):
    """
    Todos os produtos são mostrados, exceto os do próprio usuário logado
    """
    produtos = Produto.objects.exclude(vendedor=request.user)
    return render(request, 'produtos/lista_produtos.html', {'produtos': produtos})

def registrar_venda(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.vendedor = request.user
            produto.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm()
    return render(request, 'produtos/registrar_venda.html', {'form': form})

@login_required
def meus_produtos(request):
    produtos = Produto.objects.filter(vendedor=request.user)
    return render(request, 'produtos/meus_produtos.html', {'produtos': produtos})

@login_required
def remover_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, vendedor=request.user)
    if request.method =='POST':
        produto.delete()
    return redirect('meus_produtos')