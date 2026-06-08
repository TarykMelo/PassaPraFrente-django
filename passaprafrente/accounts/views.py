import random 
from pathlib import Path
import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CadastroForm, NicknameForm, TelefoneForm, SenhaForm
from produtos.models import Produto, Denuncia
from produtos.utils import ProdutosDisponiveis
from pedidos.models import Feedback, Pedido
from .two_factor import EnviarCodigo, VerificarCodigo
from .models import CodigoVerificacao, Usuario
from .recomendacoes import recomendar_produtos
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.middleware.csrf import get_token 

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

        from .models import Usuario
        usuario         = Usuario.objects.get(id=request.session['usuario_verificar_email'])
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

        from .models import Usuario
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
        recomendados = recomendar_produtos(request.user, produtos)

        return render(request, 'accounts/user_menu.html', {
            'produtos': produtos,
            'recomendados': recomendados,    
        })


def calcular_badge(user):
    vendas = user.total_avaliacoes
    media = user.media_avaliacoes

    niveis = [
        ('diamante', '💎', 'Diamante', 50, 4.6, None, None),
        ('platina',  '🔷', 'Platina',  25, 4.4, 'Diamante', (50, 4.6)),
        ('ouro',     '🥇', 'Ouro',     10, 4.0, 'Platina',  (25, 4.4)),
        ('prata',    '🥈', 'Prata',     5, 0.0, 'Ouro',     (10, 4.0)),
        ('bronze',   '🥉', 'Bronze',    0, 0.0, 'Prata',    (5, 0.0)),
    ]

    for nivel, icone, nome, min_vendas, min_media, proximo_nome, proximo_req in niveis:
        if vendas >= min_vendas and media >= min_media:
            requisitos = None
            if proximo_req:
                partes = []
                vendas_faltam = proximo_req[0] - vendas
                if vendas_faltam > 0:
                    partes.append(f'faltam {vendas_faltam} {"venda" if vendas_faltam == 1 else "vendas"}')
                if proximo_req[1] > 0 and media < proximo_req[1]:
                    partes.append(f'nota ≥ {proximo_req[1]} (atual: {media})')
                requisitos = ' e '.join(partes) if partes else None

            return {
                'badge_nivel': nivel,
                'badge_icone': icone,
                'badge_nome': nome,
                'badge_proximo': proximo_nome,
                'badge_requisitos': requisitos,
            }

    return {
        'badge_nivel': 'bronze',
        'badge_icone': '🥉',
        'badge_nome': 'Bronze',
        'badge_proximo': 'Prata',
        'badge_requisitos': 'faça sua primeira venda',
    }


class ModificarDadosView(LoginRequiredMixin, View):
    def get(self, request):
        ctx = {
            'nickname_form': NicknameForm(instance=request.user),
            'telefone_form': TelefoneForm(instance=request.user),
            'senha_form':    SenhaForm(request.user),
        }
        ctx.update(calcular_badge(request.user))
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
        ctx.update(calcular_badge(request.user))
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
        ctx.update(calcular_badge(vendedor))
        return render(request, 'accounts/perfil_vendedor.html', ctx)

class EsqueciSenhaView(View):

    def get(self, request):
        print("reset_codigo:", request.session.get('reset_codigo'))
        print("reset_user_id:", request.session.get('reset_user_id'))

        return render(request, 'accounts/esqueci_senha.html')

    def post(self, request):
        email = request.POST.get('email')

        try:
            usuario = Usuario.objects.get(email=email)

            codigo_verificacao = str(random.randint(100000, 999999))

            request.session['reset_codigo'] = codigo_verificacao
            request.session['reset_user_id'] = usuario.pk

            import smtplib
            import ssl
            from email.mime.text import MIMEText
            from django.conf import settings

            msg = MIMEText(
                f"Olá!\n\n"
                f"Você solicitou a redefinição de senha no PassaPraFrente.\n\n"
                f"Seu código de verificação é: {codigo_verificacao}\n\n"
                f"Insira este código na página do sistema para criar sua nova senha."
            )

            msg['Subject'] = "Seu Código de Verificação - PassaPraFrente"
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = email

            contexto_ssl = ssl.create_default_context()
            contexto_ssl.check_hostname = False
            contexto_ssl.verify_mode = ssl.CERT_NONE

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls(context=contexto_ssl)
                server.login(
                    settings.EMAIL_HOST_USER,
                    settings.EMAIL_HOST_PASSWORD
                )
                server.sendmail(
                    settings.EMAIL_HOST_USER,
                    [email],
                    msg.as_string()
                )

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

        if 'reset_codigo' not in request.session:
            return redirect('esqueci_senha')

        return render(request, 'accounts/esqueci_senha_codigo.html')

    def post(self, request):

        codigo_salvo = request.session.get('reset_codigo')

        if not codigo_salvo:
            return redirect('esqueci_senha')

        codigo_digitado = request.POST.get('codigo_digitado')

        if codigo_digitado == codigo_salvo:
            return redirect('nova_senha')

        return render(
            request,
            'accounts/esqueci_senha_codigo.html',
            {'erro': 'Código inválido. Tente novamente.'}
        )

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

        erros = []

        if len(nova_senha) < 8:
            erros.append("A senha precisa ter pelo menos 8 caracteres")

        if not re.search(r"[A-Z]", nova_senha):
            erros.append("A senha precisa ter pelo menos uma letra maiúscula")

        if not re.search(r"[0-9]", nova_senha):
            erros.append("A senha precisa ter pelo menos um número")

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", nova_senha):
            erros.append("A senha precisa ter pelo menos um símbolo")

        if re.search(r"\s", nova_senha):
            erros.append("A senha não pode conter espaços")

        if re.search(r"[À-ÿ]", nova_senha):
            erros.append("A senha não pode conter caracteres acentuados")

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