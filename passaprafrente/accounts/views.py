from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CadastroForm, NicknameForm, TelefoneForm, SenhaForm
from produtos.models import Produto
from produtos.utils import ProdutosDisponiveis
from .two_factor import EnviarCodigo, VerificarCodigo
from .models import CodigoVerificacao


class CadastroView(View):
    def get(self, request):
        form = CadastroForm()
        return render(request, 'accounts/cadastro.html', {'form': form})

    def post(self, request):
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_menu')
        return render(request, 'accounts/cadastro.html', {'form': form})


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        email = request.POST.get('email')
        senha = request.POST.get('password')
        user  = authenticate(request, username=email, password=senha)

        if user is not None:
            if user.dois_fatores:
                request.session['usuario_pre_auth'] = user.id
                return redirect('escolher_metodo_2fa')
            else:
                login(request, user)
                return redirect('user_menu')

        return render(request, 'accounts/login.html', {
            'erro': 'Email ou senha incorretos'
        })
    
class VerificarCodigoView(View):
    """
    Usuário digita o código recebido
    """
    def get(self, request):
        if 'usuario_pre_auth' not in request.session:
            return redirect('login')
        return render(request, 'accounts/verificar_codigo.html')
    
    def post(self, request):
        if 'usuario_pre_auth' not in request.session:
            return redirect('login')
        
        from .models import Usuario
        usuario = Usuario.objects.get(id=request.session['usuario_pre_auth'])
        codigo_digitado = request.POST.get('codigo')

        valido, mensagem = VerificarCodigo.verificar(usuario, codigo_digitado)

        if valido:
            login(request, usuario)
            del request.session['usuario_pre_auth']
            del request.session['metodo_2fa']
            return redirect('user_menu')

        return render(request, 'accounts/verificar_codigo.html', {
            'erro': mensagem
        })


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class UserMenuView(LoginRequiredMixin, View):
    def get(self, request):
        produtos = ProdutosDisponiveis.get(request.user)
        return render(request, 'accounts/user_menu.html', {'produtos': produtos})


class ModificarDadosView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/modificar_dados.html', {
            'nickname_form': NicknameForm(instance=request.user),
            'telefone_form': TelefoneForm(instance=request.user),
            'senha_form':    SenhaForm(request.user),
        })

    def post(self, request):
        nickname_form = NicknameForm(instance=request.user)
        telefone_form = TelefoneForm(instance=request.user)
        senha_form    = SenhaForm(request.user)

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
            
        elif 'toggle_2fa' in request.POST:
            request.user.dois_fatores = not request.user.dois_fatores
            request.user.save()
            status = "ativado" if request.user.dois_fatores else "desativado"
            messages.success(request, f"2FA {status} com sucesso!")
            return redirect('modificar_dados')

        return render(request, 'accounts/modificar_dados.html', {
            'nickname_form': nickname_form,
            'telefone_form': telefone_form,
            'senha_form':    senha_form,
        })


class DeletarContaView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/deletar_conta.html')

    def post(self, request):
        senha = request.POST.get('password')
        if request.user.check_password(senha):
            request.user.delete()
            logout(request)
            return redirect('login')
        return render(request, 'accounts/deletar_conta.html', {
            'erro': 'Senha incorreta'
        })
    
class EscolherMetodo2FAView(View):
    """Usuário escolhe receber por email ou SMS"""
    def get(self, request):
        if 'usuario_pre_auth' not in request.session:
            return redirect('login')
        return render(request, 'accounts/escolher_metodo_2fa.html')

    def post(self, request):
        if 'usuario_pre_auth' not in request.session:
            return redirect('login')

        from .models import Usuario
        usuario = Usuario.objects.get(id=request.session['usuario_pre_auth'])
        metodo  = request.POST.get('metodo')

        try:
            if metodo == 'email':
                EnviarCodigo.por_email(usuario)
            elif metodo == 'sms':
                EnviarCodigo.por_sms(usuario)
        except Exception as e:
            return render(request, 'accounts/escolher_metodo_2fa.html', {
                'erro': f'Erro ao enviar código: {e}'
            })

        request.session['metodo_2fa'] = metodo
        return redirect('verificar_codigo')