from django.urls import path
from .views import (
    ListaProdutosView, RegistrarVendaView, MeusProdutosView, 
    RemoverProdutoView, CategoriaView, TodasCategoriasView
) 

urlpatterns = [
    path('menu/', ListaProdutosView.as_view(), name='user_menu'),
    path('vender/', RegistrarVendaView.as_view(), name='registrar_venda'),
    path('meus-produtos/', MeusProdutosView.as_view(), name='meus_produtos'),
    path('remover/<int:produto_id>/', RemoverProdutoView.as_view(), name='remover_produto'),
    path('categoria/<str:categoria>/', CategoriaView.as_view(), name='categoria_view'),
    path('categorias/', TodasCategoriasView.as_view(), name='todas_categorias'),
]