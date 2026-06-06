from django.urls import path
from .views import NotificacoesView, LimparNotificacoes

urlpatterns = [
    path('', NotificacoesView.as_view(), name='notificacoes'),
    path('limpar/', LimparNotificacoes.as_view(), name='limpar_notificacoes'),
]


