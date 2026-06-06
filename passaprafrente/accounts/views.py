import random 
from pathlib import Path
import os
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
        recomendados = recomendar_produtos(request.user, produtos)

        return render(request, 'accounts/user_menu.html', {
            'produtos': produtos,
            'recomendados': recomendados,    
        })


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

        return render(request, 'accounts/perfil_vendedor.html',{
            'vendedor': vendedor,
            'feedbacks': feedbacks,
            'denuncias': denuncias,
            'total_finalizados': total_finalizados,
            'denuncias_confirmadas': denuncias_confirmadas,
            'voltar': voltar,
        })

class EsqueciSenhaView(View):
    def get(self, request):
        csrf_token = get_token(request)
        return HttpResponse(f'''
            <div style="max-width: 400px; margin: 50px auto; font-family: sans-serif; text-align: center;">
                <h2>Recuperar Senha</h2>
                <form method="POST" style="display: flex; flex-direction: column; gap: 15px;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                    <input type="email" name="email" placeholder="Digite seu email cadastrado" style="padding: 10px;" required>
                    <button type="submit" style="padding: 10px; background: #007bff; color: white; border: none; cursor: pointer;">Enviar Link de Recuperação</button>
                </form>
            </div>
        ''')

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

            msg = MIMEText(f"Olá!\n\nVocê solicitou a redefinição de senha no PassaPraFrente.\n\nSeu código de verificação é: {codigo_verificacao}\n\nInsira este código na página do sistema para criar sua nova senha.\n\nSe não foi você quem pediu, pode ignorar este e-mail com segurança.")
            msg['Subject'] = "Seu Código de Verificação - PassaPraFrente"
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = email   

            contexto_ssl = ssl.create_default_context() 
            contexto_ssl.check_hostname = False        
            contexto_ssl.verify_mode = ssl.CERT_NONE

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls(context=contexto_ssl) 
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(settings.EMAIL_HOST_USER, [email], msg.as_string())

                return redirect('/esqueci-a-senha/verificar-codigo/')

        except Usuario.DoesNotExist: 
            return HttpResponse('<div style="max-width: 500px; margin: 50px auto; font-family: sans-serif; text-align: center; color: red;"><h2>O e-mail digitado não está cadastrado.</h2><a href="">Tentar novamente</a></div>')
        except Exception as e: 
            return HttpResponse(f'<div style="max-width: 500px; margin: 50px auto; font-family: sans-serif; text-align: center; color: red;"><h2>Erro ao disparar o e-mail técnico: {e}</h2><p>Verifique as credenciais no seu arquivo .env</p></div>')
            
           
class VerificarCodigoView(View):
    def get(self, request):
        csrf_token = get_token(request)
        return HttpResponse(f'''
            <div style="max-width: 400px; margin: 50px auto; font-family: sans-serif; text-align: center;">
                <h2>Digite o Código</h2>
                <p style="color: #666;">Insira o código de 6 dígitos enviado para o seu e-mail.</p>
                <form method="POST" style="display: flex; flex-direction: column; gap: 15px; margin-top: 20px;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                    <input type="text" name="codigo_digitado" placeholder="Ex: 123456" maxlength="6" style="padding: 10px; text-align: center; font-size: 18px;" required>
                    <button type="submit" style="padding: 10px; background: #28a745; color: white; border: none; cursor: pointer; font-weight: bold;">Verificar Código</button>
                </form>
            </div>
        ''')

    def post(self, request):
        codigo_digitado = request.POST.get('codigo_digitado')
        codigo_salvo = request.session.get('reset_codigo')
        
        if codigo_salvo and codigo_digitado == codigo_salvo:
            return redirect('/esqueci-a-senha/nova-senha/')
        else:
             return HttpResponse('<div style="max-width: 500px; margin: 50px auto; font-family: sans-serif; text-align: center; color: red;"><h2>❌ Código inválido ou expirado!</h2><a href="/esqueci-a-senha/verificar-codigo/">Tentar novamente</a></div>')


class NovaSenhaView(View):
    def get(self, request):
        if 'reset_user_id' not in request.session:
            return redirect('/esqueci-a-senha/')
            
        csrf_token = get_token(request)
        return HttpResponse(f'''
            <div style="max-width: 400px; margin: 50px auto; font-family: sans-serif; text-align: center;">
                <h2>Definir Nova Senha</h2>
                <form method="POST" style="display: flex; flex-direction: column; gap: 15px; margin-top: 20px;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                    <input type="password" name="nova_senha" placeholder="Digite sua nova senha" style="padding: 10px;" required>
                    <button type="submit" style="padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; font-weight: bold;">Salvar Nova Senha</button>
                </form>
            </div>
        ''')

    def post(self, request):
        user_id = request.session.get('reset_user_id')
        if not user_id:
            return redirect('/esqueci-a-senha/')
            
        try:
            usuario = Usuario.objects.get(pk=user_id)
            nova_senha = request.POST.get('nova_senha')
            
            usuario.set_password(nova_senha)
            usuario.save()
            
            request.session.flush()  # Limpa a sessão por segurança
            
            return HttpResponse('''
                <div style="max-width: 500px; margin: 50px auto; font-family: sans-serif; text-align: center; border: 2px solid #28a745; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #28a745;">✅ Senha alterada com sucesso!</h2>
                    <p style="margin-bottom: 20px;">O banco de dados foi atualizado com a nova senha.</p>
                    <p><a href="/" style="background: #007bff; color: white; padding: 12px 20px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block;">IR PARA O LOGIN</a></p>
                </div>
            ''')
        except Exception as e:
            return HttpResponse(f"Erro ao salvar senha: {e}")