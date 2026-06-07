from django.urls import path
from .views import (
    CadastroView, LoginView, LogoutView,
    UserMenuView, ModificarDadosView, DeletarContaView,
    EscolherMetodo2FAView, VerificarCodigoView, PerfilVendedorView,
    EsqueciSenhaView, EsqueciSenhaCodigoView, NovaSenhaView
    )

urlpatterns = [
    path('login/', LoginView.as_view(), name='login_aba'),
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('sair/', LogoutView.as_view(), name='logout'),
    path('menu/', UserMenuView.as_view(), name='user_menu'),
    path('conta/', ModificarDadosView.as_view(), name='modificar_dados'),
    path('conta/deletar/', DeletarContaView.as_view(), name='deletar_conta'),
    path('2fa/metodo/', EscolherMetodo2FAView.as_view(), name='escolher_metodo_2fa'),
    path('2fa/verificar/', VerificarCodigoView.as_view(), name='verificar_codigo'),
    path('conta/vendedor/<int:id>/', PerfilVendedorView.as_view(), name='perfil_vendedor'),
    path('esqueci-a-senha/', EsqueciSenhaView.as_view(), name='esqueci_senha'),
    path('esqueci-a-senha/verificar-codigo/', EsqueciSenhaCodigoView.as_view(), name='esqueci_senha_codigo'),
    path('esqueci-a-senha/nova-senha/', NovaSenhaView.as_view(), name='nova_senha'),
]