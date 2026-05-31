from django.urls import path
from .views import (
    FazerPedidoView, MeusPedidosView, CancelarPedidoView, 
    EnviarFeedbackView, MinhasVendasView, MudarStatusVendaView,
    ConfirmarRecebimentoView, MeusFeedbacksView, HistoricoView,
    HistoricoComprasView, HistoricoVendasView, DetalheHistoricoView
)

urlpatterns = [
    path('fazer/<int:produto_id>/',   FazerPedidoView.as_view(),   name='fazer_pedido'),
    path('meus/',                     MeusPedidosView.as_view(),   name='meus_pedidos'),
    path('cancelar/<int:pedido_id>/', CancelarPedidoView.as_view(), name='cancelar_pedido'),
    path('feedback/<int:pedido_id>/', EnviarFeedbackView.as_view(), name='enviar_feedback'),
    path('vendas/',                    MinhasVendasView.as_view(),   name='minhas_vendas'),
    path('vendas/status/<int:pedido_id>/', MudarStatusVendaView.as_view(),   name='mudar_status_venda'),
    path('vendas/status/<int:pedido_id>', ConfirmarRecebimentoView.as_view(), name='confirmar_recebimento'),
    path('feedbacks/', MeusFeedbacksView.as_view(), name='meus_feedbacks'),
    path('historico/', HistoricoView.as_view(), name='historico'),
    path('historico/compras/', HistoricoComprasView.as_view(), name='historico_compras'),
    path('historico/vendas/', HistoricoVendasView.as_view(), name='historico_vendas'),
    path('historico/detalhe/<int:pedido_id>/', DetalheHistoricoView.as_view(), name='detalhe_historico')
]