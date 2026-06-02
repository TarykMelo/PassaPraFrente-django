from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from produtos.models import Produto, Denuncia 
from .forms import ProdutoForm
from produtos.utils import ProdutosDisponiveis

class ListaProdutosView(LoginRequiredMixin, View):
    """
    Todos os produtos são exibidos, excetoos do próprio usuário
    """

    def get(self, request):
        produtos = Produto.objects.exclude(vendedor=request.user)
        return render(request, 'accounts/user_menu.html', {'produtos': produtos})

class RegistrarVendaView(LoginRequiredMixin, View):
    def get(self, request): 
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
        produtos = Produto.objects.filter(
            vendedor=request.user,
            vendido=False
        )
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
        produtos = ProdutosDisponiveis.get(request.user, categoria=categoria)
        return render(request, 'produtos/categoria.html', {
            'produtos': produtos,
            'categoria_atual': categoria,
        })


class TodasCategoriasView(LoginRequiredMixin, View):
    """
    Permite ver todos os produtos na página 'categoria'
    """
    def get(self, request):
        produtos = ProdutosDisponiveis.get(request.user)
        return render(request, 'produtos/categoria.html', {
            'produtos': produtos,
            'categoria_atual': None, 
        })
    

class DenunciarProdutoView(LoginRequiredMixin, View):
    """
    Processa a denúncia de um produto enviada via formulário POST
    """
    def post(self, request, produto_id): 
        produto = get_object_or_404(Produto, id=produto_id)

        if produto.vendedor == request.user: 
            messages.error(request, "Você não pode denunciar o seu próprio produto!")
            return redirect('user_menu')
        
        motivo = request.POST.get('motivo')
        descricao = request.POST.get('descricao')

        Denuncia.objects.create(
            usuario=request.user,
            produto=produto,
            motivo=motivo, 
            descricao=descricao
        )

        messages.success(request, "Denúncia registrada. Nossa equipe irá analisar!")
        return redirect('user_menu')