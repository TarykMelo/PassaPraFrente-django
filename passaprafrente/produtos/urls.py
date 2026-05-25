from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_produtos, name='lista_produtos'),
    path('vender/', views.registrar_venda, name='registrar_venda'),
    path('meus/', views.meus_produtos, name='meus_produtos'),
    path('remover/<int:produto_id>/', views.remover_produto, name='remover_produto'),
    path('categoria<str:categoria>/', views.categoria_view, name='categoria'),
    path('categoria/', views.todas_categorias, name='todas_categorias'),
]