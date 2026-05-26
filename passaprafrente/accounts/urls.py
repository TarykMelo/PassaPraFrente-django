from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('sair/', views.logout_view, name='logout'),
    path('menu', views.user_menu_view, name='user_menu'),
    path('conta/nickname/', views.modificar_nickname, name='modificar_nickname'),
    path('conta/telefone/', views.modificar_telefone, name='modificar_telefone'),
    path('conta/senha/', views.modificar_senha, name='modificar_senha'),
    path('conta/deletar/', views.deletar_conta, name='deletar_conta'),
    ]