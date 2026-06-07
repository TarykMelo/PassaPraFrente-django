import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def enviar_email_status_pedido(email_destinatario, nome_comprador, nome_produto, numero_pedido, status):
    """
    Dispara um e-mail real usando smtplib contornando os erros de SSL do Windows.
    """
    remetente = os.getenv('EMAIL_USER')
    senha_app = os.getenv('EMAIL_PASSWORD')
    
    if not remetente or not senha_app:
        print("Erro: Credenciais de e-mail não configuradas no arquivo .env")
        return False

    
    if status == 'confirmado':
        assunto = f"Boas notícias! Seu pedido #{numero_pedido} foi aceito! 🎉"
        corpo = f"Olá, {nome_comprador}!\n\nO vendedor aceitou o seu pedido para o produto '{nome_produto}' (Pedido #{numero_pedido}).\nEm breve você receberá novas atualizações sobre o andamento e a entrega!"
    elif status == 'cancelado':
        assunto = f"Atualização sobre o seu pedido #{numero_pedido} 😔"
        corpo = f"Olá, {nome_comprador}.\n\nInfelizmente o vendedor precisou cancelar o seu pedido para o produto '{nome_produto}' (Pedido #{numero_pedido}).\nSe você realizou algum pagamento, o processo de estorno será iniciado."
    else:
        return False


    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = email_destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))


    contexto = ssl.create_default_context()
    contexto.check_hostname = False
    contexto.verify_mode = ssl.CERT_NONE

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(context=contexto)
        server.login(remetente, senha_app)
        server.sendmail(remetente, email_destinatario, msg.as_string())
        server.quit()
        print(f"E-mail enviado com sucesso para {email_destinatario}!")
        return True
    except Exception as e:
        print(f"Falha ao enviar e-mail via smtplib: {e}")
        return False