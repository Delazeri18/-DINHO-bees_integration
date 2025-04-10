import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging

def send_email_with_attachment(subject, body, recipient, attachment_path):
    sender = ""
    password = ""
    
    # Criar a mensagem
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Adicionar anexo
    try:
        with open(attachment_path, 'rb') as file:
            part = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{attachment_path.split("/")[-1]}"'
            )
            msg.attach(part)
    except Exception as e:
        print(f"Erro ao anexar o arquivo: {e}")
        return
    
    # Enviar e-mail usando SMTP_SSL
    try:
        with smtplib.SMTP_SSL('smtp.skymail.net.br', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        logging.info("E-mail enviado com sucesso!")
    except Exception as e:
        logging.info(f"Erro ao enviar o e-mail: {e}")

def send_email(subject, body, recipient):
    sender = ""
    password = ""
    
    # Criar a mensagem
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    
    # Enviar e-mail usando SMTP_SSL
    try:
        with smtplib.SMTP_SSL('smtp.skymail.net.br', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        logging.info("E-mail enviado com sucesso!")
    except Exception as e:
        logging.info(f"Erro ao enviar o e-mail: {e}")
