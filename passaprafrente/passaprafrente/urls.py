"""
URL configuration for passaprafrente project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from accounts.views import LoginView, EsqueciSenhaView, VerificarCodigoView, NovaSenhaView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('esqueci-a-senha/', EsqueciSenhaView.as_view(), name='password_reset'),
    path('esqueci-a-senha/verificar-codigo/', VerificarCodigoView.as_view(), name='verificar_codigo'),
    path('esqueci-a-senha/nova-senha/', NovaSenhaView.as_view(), name='nova_senha'),
    path('produtos/', include('produtos.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('', LoginView.as_view(), name='login'),
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)