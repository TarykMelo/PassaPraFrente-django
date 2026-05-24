from django.urls import path
from . import views

urlpatterns = [
    path('fazer/<int:produto_id>/', views.fazer_pedido, name='fazer_pedido'),
    path('meus/', views.meus_pedidos, name='meus_pedidos'),
    path('cancelar/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
]
