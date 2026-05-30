from django.urls import path
from .views import FazerPedidoView, MeusPedidosView, CancelarPedidoView, EnviarFeedbackView, MinhasVendasView

urlpatterns = [
    path('fazer/<int:produto_id>/',   FazerPedidoView.as_view(),   name='fazer_pedido'),
    path('meus/',                     MeusPedidosView.as_view(),   name='meus_pedidos'),
    path('cancelar/<int:pedido_id>/', CancelarPedidoView.as_view(), name='cancelar_pedido'),
    path('feedback/<int:pedido_id>/', EnviarFeedbackView.as_view(), name='enviar_feedback'),
    path('vendas/',                    MinhasVendasView.as_view(),   name='minhas_vendas'),
    path('vendas/status/<int:pedido_id>/', MinhasVendasView.as_view(),   name='mudar_status_venda'),]