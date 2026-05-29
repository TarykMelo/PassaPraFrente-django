from django.urls import path
from .views import (
    CadastroView, LoginView, LogoutView,
    UserMenuView, ModificarDadosView, DeletarContaView
)

urlpatterns = [
    path('',               LoginView.as_view(),        name='login'),
    path('cadastro/',      CadastroView.as_view(),      name='cadastro'),
    path('sair/',          LogoutView.as_view(),        name='logout'),
    path('menu/',          UserMenuView.as_view(),      name='user_menu'),
    path('conta/',         ModificarDadosView.as_view(), name='modificar_dados'),
    path('conta/deletar/', DeletarContaView.as_view(),  name='deletar_conta'),
]