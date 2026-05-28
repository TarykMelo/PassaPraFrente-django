from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from produtos.models import Produto
from .forms import ProdutoForm

class ListaProdutosView(LoginRequiredMixin, View):
    """
    Todos os produtos são exibidos, excetoos do próprio usuário
    """

    def get(self, request):
        produtos = Produto.objects.exclude(vendedor=request.user)
        return render(request, 'produtos/user_menu.html', {'produtos': produtos})

class RegistrarVendaView(LoginRequiredMixin, View):
    def ger(self, request): 
        form = ProdutoForm()
        return render(request, 'produtos/registrar_venda.html', {'form': form})
    
    def post(self, request):
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.vendedor = request.user
            produto.save()
            return redirect('user_menu')
        return render(request, 'produtos/registrar_venda.html', {'form': form})


class MeusProdutosView(LoginRequiredMixin, View):
    def get(self, request):
        produtos = Produto.objects.filter(vendedor=request.user)
        return render(request, 'produtos/meus_produtos.html', {'produtos': produtos})


class RemoverProdutoView(LoginRequiredMixin, View):
    def post(self, request, produto_id):
        produto = get_object_or_404(Produto, id=produto_id, vendedor=request.user)
        produto.delete()
        return redirect('meus_produtos')


class CategoriaView(LoginRequiredMixin, View):
    """
    Filtrar produtos por categoria
    """
    def get(self, request, categoria):
        produtos = Produto.objects.exclude(vendedor=request.user).filter(categoria=categoria)
        return render(request, 'produtos/categoria.html', {
            'produtos': produtos,
            'categoria_atual': categoria,
        })


class TodasCategoriasView(LoginRequiredMixin, View):
    """
    Permite ver todos os produtos na página 'categoria'
    """
    def get(self, request):
        produtos = Produto.objects.exclude(vendedor=request.user)
        return render(request, 'produtos/categoria.html', {
            'produtos': produtos,
            'categoria_atual': None, 
        })

