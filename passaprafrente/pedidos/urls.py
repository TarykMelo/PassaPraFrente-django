from django.urls import path
from .views import FazerPedidoView, MeusPedidosView, CancelarPedidoView

urlpatterns = [
    path('fazer/<int:produto_id>/',   FazerPedidoView.as_view(),   name='fazer_pedido'),
    path('meus/',                     MeusPedidosView.as_view(),   name='meus_pedidos'),
    path('cancelar/<int:pedido_id>/', CancelarPedidoView.as_view(), name='cancelar_pedido'),
]