import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

EMAIL_HOST = os.getenv("EMAIL_HOST")          # Servidor SMTP (ex.: smtp.gmail.com)
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))     # Porta do servidor SMTP (ex.: 587)
EMAIL_USER = os.getenv("EMAIL_USER")          # Seu e-mail
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Senha do e-mail
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # E-mail da secretária

# Função para enviar e-mail com anexo
def send_email_with_attachment(file_form, file_comprovantes, name, dre, email):
    try:
        # Configurar e-mail
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Relatório de Estágio - {dre}"
        msg.attach(MIMEText("Segue o relatório de estágio em anexo.", 'plain'))

        msg.attach(MIMEText(f"Nome: {name}", 'plain'))
        msg.attach(MIMEText(f"DRE: {dre}", 'plain'))
        msg.attach(MIMEText(f"E-MAIL: {email}", 'plain'))

        # Adicionar form
        with open(file_form, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(file_form)}")
        msg.attach(part)

        # Adicionar comprovantes
        for arquivo in file_comprovantes: 
            with open(arquivo, 'rb') as anexo: 
                parte = MIMEBase('application', 'octet-stream') 
                parte.set_payload(anexo.read()) 
            encoders.encode_base64(parte) 
            parte.add_header('Content-Disposition', f'attachment; filename={os.path.basename(arquivo)}') 
            msg.attach(parte)

        # Conectar ao servidor e enviar e-mail
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"E-mail enviado com sucesso para {RECIPIENT_EMAIL}.")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False
