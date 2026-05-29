from django.urls import path
from . import views

urlpatterns = [
    path('<int:pedido_id>/', views.chat_pedido, name='chat_pedido'),
    path('<int:pedido_id>/novas/', views.mensagens_novas, name='mensagens_novas'),
]