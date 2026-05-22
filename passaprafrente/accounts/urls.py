from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('sair/', views.logout_view, name='logout'),
    path('menu', views.user_menu_view, name='user_menu'),
]