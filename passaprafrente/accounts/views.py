from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm, NicknameForm, TelefoneForm, SenhaForm
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

@login_required
def modificar_dados(request):
    """
    Função para levar para a aba de modificar os dados
    """
    return render(request, 'accounts/modificar_dados.html')

@login_required
def modificar_nickname(request):
    """
    Função para modificar o nickname do usuário
    """
    if request.method == 'POST':
        form = NicknameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('modificar_dados')
    else:
        form = NicknameForm(instance=request.user)
    return render(request, 'accounts/modificar_nickname.html', {'form': form})

@login_required
def modificar_telefone(request):
    """
    Função para modificar o telefone do usuário
    """
    if request.method == 'POST':
        form = TelefoneForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('modificar_dados')
    else:
        form = TelefoneForm(instance=request.user)
    return render(request, 'accounts/modificar_telefone.html', {'form': form})

@login_required
def modificar_senha(request):
    """
    Função para modificar a senha do usuário
    """
    if request.method == 'POST':
        form = SenhaForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('modificar_dados')
    else:
        form = SenhaForm(request.user)
    return render(request, 'accounts/modificar_senha.html', {'form': form})

@login_required
def deletar_conta(request):
    """
    Função para deletar a conta do usuário
    """
    if request.method == 'POST':
        form = SenhaForm(request.user, request.POST)
        if form.is_valid():
            request.user.delete()
            logout(request)
            return redirect('login')
    else:
        form = SenhaForm(request.user)
    return render(request, 'accounts/deletar_conta.html', {'form': form})