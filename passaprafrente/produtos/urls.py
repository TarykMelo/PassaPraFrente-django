from django.urls import path
from .views import (
    ListaProdutosView, RegistrarVendaView, MeusProdutosView, 
    RemoverProdutoView, CategoriaView, TodasCategoriasView, DenunciarProdutoView,
    ModificarProdutoView
) 

urlpatterns = [
    path('menu/', ListaProdutosView.as_view(), name='lista_produtos'),
    path('vender/', RegistrarVendaView.as_view(), name='registrar_venda'),
    path('meus-produtos/', MeusProdutosView.as_view(), name='meus_produtos'),
    path('remover/<int:produto_id>/', RemoverProdutoView.as_view(), name='remover_produto'),
    path('categoria/<str:categoria>/', CategoriaView.as_view(), name='categoria'),
    path('categorias/', TodasCategoriasView.as_view(), name='todas_categorias'),
    path('produto/<int:produto_id>/denunciar/', DenunciarProdutoView.as_view(), name='denunciar_produto'),
    path('produto/modificar/<int:produto_id>/', ModificarProdutoView.as_view(), name='modificar_produto'),
]