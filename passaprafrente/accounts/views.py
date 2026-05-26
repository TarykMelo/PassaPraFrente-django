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
    Função para levar para modificar os dados do usuário
    """
    nickname_form = NicknameForm(instance=request.user)
    telefone_form = TelefoneForm(instance=request.user)
    senha_form = SenhaForm(request.user)

    if request.method == 'POST':
        if 'salvar_nickname' in request.POST:
            nickname_form = NicknameForm(request.POST, instance=request.user)
            if nickname_form.is_valid():
                nickname_form.save()
                return redirect('modificar_dados')
            
        elif 'salvar_telefone' in request.POST:
            telefone_form = TelefoneForm(request.POST, instance=request.user)
            if telefone_form.is_valid():
                telefone_form.save()
                return redirect('modificar_dados')
        
        elif 'salvar_senha' in request.POST:
            senha_form = SenhaForm(request.user, request.POST)
            if senha_form.is_valid():
                user = senha_form.save()
                update_session_auth_hash(request, user)
                return redirect('modificar_dados')
    return render(request, 'accounts/modificar_dados.html', {
        'nickname_form': nickname_form,
        'telefone_form': telefone_form,
        'senha_form': senha_form,
    })
        
@login_required
def deletar_conta(request):
    """
    Função para deletar a conta do usuário
    """
    if request.method == 'POST':
        senha = request.POST.get('password')
        if request.user.check_password(senha):
            request.user.delete()
            logout(request)
            return redirect('login')
        else:
            return render(request, 'accounts/deletar_conta.html',{
                'erro': 'Senha incorreta'
            })
    return render(request, 'accounts/deletar_conta.html')