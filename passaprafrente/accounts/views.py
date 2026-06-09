import random 
from pathlib import Path
import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CadastroForm, NicknameForm, TelefoneForm, SenhaForm, validar_senha
from produtos.models import Produto, Denuncia
from produtos.utils import ProdutosDisponiveis
from pedidos.models import Feedback, Pedido
from .two_factor import EnviarCodigo, VerificarCodigo
from .models import CodigoVerificacao, Usuario
from .recomendacoes import recomendar_produtos
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.middleware.csrf import get_token
from .badge import Badge
import smtplib
import ssl
from email.mime.text import MIMEText

class CadastroView(View):
    def get(self, request):
        form = CadastroForm()
        return render(request, 'accounts/cadastro.html', {'form': form})

    def post(self, request):
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            EnviarCodigo.por_email(user)
            request.session['usuario_verificar_email'] = user.id
            return redirect('verificar_email')
        return render(request, 'accounts/cadastro.html', {'form': form})

class VerificarEmailView(View):
    """
    Verifica o email do usuário após o cadastro
    """
    def get(self, request):
        if 'usuario_verificar_email' not in request.session:
            return redirect('cadastro')
        return render(request, 'accounts/verificar_email.html')

    def post(self, request):
        if 'usuario_verificar_email' not in request.session:
            return redirect('cadastro')

        usuario = Usuario.objects.get(id=request.session['usuario_verificar_email'])
        codigo_digitado = request.POST.get('codigo')

        valido, mensagem = VerificarCodigo.verificar(usuario, codigo_digitado)

        if valido:
            usuario.email_verificado = True
            usuario.save()
            login(request, usuario)
            del request.session['usuario_verificar_email']
            return redirect('user_menu')

        return render(request, 'accounts/verificar_email.html', {
            'erro': mensagem
        })


class ReenviarCodigoEmailView(View):
    """
    Reenvia o código de verificação de email
    """
    def post(self, request):
        if 'usuario_verificar_email' not in request.session:
            return redirect('cadastro')

        usuario = Usuario.objects.get(id=request.session['usuario_verificar_email'])
        EnviarCodigo.por_email(usuario)
        return render(request, 'accounts/verificar_email.html', {
            'sucesso': 'Código reenviado com sucesso!'
        })


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        email = request.POST.get('email')
        senha = request.POST.get('password')
        user  = authenticate(request, username=email, password=senha)

        if user is not None:

            if not user.email_verificado:
                EnviarCodigo.por_email(user)
                request.session['usuario_verificar_email'] = user.id
                return redirect('verificar_email')
            
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
        recomendados = recomendar_produtos(request.user, produtos)

        return render(request, 'accounts/user_menu.html', {
            'produtos': produtos,
            'recomendados': recomendados,    
        })

class ModificarDadosView(LoginRequiredMixin, View):
    def get(self, request):
        ctx = {
            'nickname_form': NicknameForm(instance=request.user),
            'telefone_form': TelefoneForm(instance=request.user),
            'senha_form':    SenhaForm(request.user),
        }
        ctx.update(Badge(request.user).calcular())
        return render(request, 'accounts/modificar_dados.html', ctx)

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

        ctx = {
            'nickname_form': nickname_form,
            'telefone_form': telefone_form,
            'senha_form':    senha_form,
        }
        ctx.update(Badge(request.user).calcular())
        return render(request, 'accounts/modificar_dados.html', ctx)


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
    

class PerfilVendedorView(View):
    def get(self, request, id):
        vendedor = get_object_or_404(Usuario, id=id)

        feedbacks = Feedback.objects.filter(
            vendedor=vendedor
        ).select_related(
            'avaliador',
            'pedido'
        )

        denuncias = Denuncia.objects.filter(
            produto__vendedor=vendedor
        )

        total_finalizados = Pedido.objects.filter(
            vendedor=vendedor,
            status='finalizado'
        ).count()

        denuncias_confirmadas = denuncias.count()

        voltar = request.GET.get('voltar', '/')

        ctx = {
            'vendedor': vendedor,
            'feedbacks': feedbacks,
            'denuncias': denuncias,
            'total_finalizados': total_finalizados,
            'denuncias_confirmadas': denuncias_confirmadas,
            'voltar': voltar,
        }
        ctx.update(Badge(vendedor).calcular())
        return render(request, 'accounts/perfil_vendedor.html', ctx)

class EsqueciSenhaView(View):

    def get(self, request):

        return render(request, 'accounts/esqueci_senha.html')

    def post(self, request):
        email = request.POST.get('email')

        try:
            usuario = Usuario.objects.get(email=email)
            codigo = EnviarCodigo.por_email(usuario)
            request.session['reset_codigo'] = codigo
            request.session['reset_user_id'] = usuario.pk
            return redirect('esqueci_senha_codigo')

        except Usuario.DoesNotExist:
            return render(
                request,
                'accounts/esqueci_senha.html',
                {'erro': 'O e-mail informado não está cadastrado.'}
            )

        except Exception as e:
            return render(
                request,
                'accounts/esqueci_senha.html',
                {'erro': f'Erro ao enviar o e-mail: {e}'}
            )
            
           
class EsqueciSenhaCodigoView(View):

    def get(self, request):
        if 'reset_user_id' not in request.session:
            return redirect('esqueci_senha')
        return render(request, 'accounts/esqueci_senha_codigo.html')

    def post(self, request):
        user_id = request.session.get('reset_user_id')

        if not user_id:
            return redirect('esqueci_senha')

        codigo_digitado = request.POST.get('codigo_digitado')

        try:
            usuario = Usuario.objects.get(pk=user_id)
            valido, mensagem = VerificarCodigo.verificar(usuario, codigo_digitado)

            if valido:
                return redirect('nova_senha')

            return render(
                request,
                'accounts/esqueci_senha_codigo.html',
                {'erro': mensagem}
            )

        except Usuario.DoesNotExist:
            return redirect('esqueci_senha')

class NovaSenhaView(View):

    def get(self, request):

        if 'reset_user_id' not in request.session:
            return redirect('esqueci_senha')

        return render(request, 'accounts/nova_senha.html')

    def post(self, request):

        user_id = request.session.get('reset_user_id')

        if not user_id:
            return redirect('esqueci_senha')

        nova_senha = request.POST.get('nova_senha')

        erros = validar_senha(nova_senha)

        if erros:
            return render(
                request,
                'accounts/nova_senha.html',
                {'erros': erros}
            )

        try:
            usuario = Usuario.objects.get(pk=user_id)

            usuario.set_password(nova_senha)
            usuario.save()

            request.session.flush()

            return render(
                request,
                'accounts/senha_alterada_sucesso.html'
            )

        except Exception as e:
            return render(
                request,
                'accounts/nova_senha.html',
                {'erros': [f'Erro ao salvar senha: {e}']}
            )