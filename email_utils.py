# ================= email_utils.py =================
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from io import BytesIO
import config

def crear_mensaje_base(asunto, destinatario):
    """Crea la estructura base del mensaje para UN destinatario"""
    msg = MIMEMultipart("related")
    msg["Subject"] = asunto
    msg["From"] = config.EMAIL_FROM
    msg["To"] = destinatario
    msg["Reply-To"] = config.EMAIL_FROM
    return msg

def crear_alternativa(texto_plano, html):
    """Crea la parte alternativa del mensaje"""
    msg_alternative = MIMEMultipart("alternative")
    msg_alternative.attach(MIMEText(texto_plano, "plain", "utf-8"))
    msg_alternative.attach(MIMEText(html, "html", "utf-8"))
    return msg_alternative

def adjuntar_imagen(msg, buffer, content_id=None, filename=None, inline=True):
    """Adjunta una imagen al mensaje"""
    buffer.seek(0)
    img = MIMEImage(buffer.read())
    
    if inline and content_id:
        img.add_header("Content-ID", f"<{content_id}>")
        img.add_header("Content-Disposition", "inline")
    elif filename:
        img.add_header("Content-Disposition", f"attachment; filename={filename}")
    else:
        img.add_header("Content-Disposition", "inline")
    
    img.add_header("Content-Type", "image/png")
    msg.attach(img)

def enviar_email_individual(msg, destinatario):
    """Envía un email a un destinatario específico"""
    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as s:
            s.starttls()
            s.login(config.EMAIL_FROM, config.SMTP_PASS)
            s.send_message(msg)
        print(f"  ✅ Enviado a {destinatario}")
        return True
    except Exception as e:
        print(f"  ❌ Error con {destinatario}: {e}")
        return False