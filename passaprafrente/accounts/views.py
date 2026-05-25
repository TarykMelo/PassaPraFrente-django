from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm
from produtos.models import Produto


def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_menu')
    else:
        form = CadastroForm()
    return render(request, 'accounts/cadastro.html', {'form': form})

def login_view(request):
    erro = None
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('password')
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            login(request, user)
            return redirect('user_menu')
        else:
            erro = "Email ou senha incorretos"
    
    return render(request, 'accounts/login.html', {'erro': erro})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_menu_view(request):
    produtos = Produto.objects.exclude(vendedor=request.user)
    return render(request, 'accounts/user_menu.html', {'produtos': produtos})

