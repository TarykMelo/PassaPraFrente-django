from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from .models import CodigoVerificacao

class EnviarCodigo:

    @staticmethod
    def por_email(usuario):
        """
        Envia o código por email
        """
        codigo = CodigoVerificacao.gerar_codigo()
        CodigoVerificacao.objects.create(
            usuario=usuario,
            codigo=codigo,
            metodo='email'
        )
        send_mail(
            subject='PassaPraFrente - Código de verificação',
            message=f'Seu código de verificação é: {codigo}\n Ele expira em 10 minutos.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[usuario.email],
        )
        return codigo
    
    @staticmethod
    def por_sms(usuario):
        """
        Envia o código por SMS
        """
        codigo = CodigoVerificacao.gerar_codigo()
        CodigoVerificacao.objects.create(
            usuario=usuario,
            codigo=codigo,
            metodo='sms'
        )
        cliente = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        cliente.messages.create(
            body=f'PassaPraFrente - Seu código de verificação é: {codigo}. Expira em 10 minutos.',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=f'+55{usuario.telefone}'
        )
        return codigo

class VerificarCodigo:

    @staticmethod
    def verificar(usuario, codigo_digitado):
        """
        Verifica se o código está correto e não expirou
        """
        try:
            codigo = CodigoVerificacao.objects.filter(
                usuario=usuario,
                codigo=codigo_digitado,
                usado=False
            ).latest('criado_em')

            if codigo.expirado():
                return False, "Código expirado, solicite um novo"
            
            codigo.usado = True
            codigo.save()
            return True, "Código válido!"
        
        except CodigoVerificacao.DoesNotExist:
            return False, "Código inválido"