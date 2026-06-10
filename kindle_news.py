import os
import smtplib
import feedparser
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

DIARIOS_MEXICO = {
    "La Jornada": "https://jornada.com.mx",
    "Excélsior": "https://excelsior.com.mx",
    "Milenio": "https://milenio.com"
}

# Variables de entorno
EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")     
PASSWORD_EMISOR = os.environ.get("PASSWORD_EMISOR") 
EMAIL_KINDLE = os.environ.get("EMAIL_KINDLE")

def generar_periodico_html():
  

def enviar_a_kindle(contenido_html):
    if not EMAIL_EMISOR or not PASSWORD_EMISOR or not EMAIL_KINDLE:
        raise ValueError("Faltan configurar variables de entorno.")

    nombre_archivo = "Prensa_Mexico.html"

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(contenido_html)

    msg = MIMEMultipart()
    msg['From'] = EMAIL_EMISOR.strip()
    msg['To'] = EMAIL_KINDLE.strip()
    msg['Subject'] = "Convertir"

    with open(nombre_archivo, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{nombre_archivo}"'
        )
        msg.attach(part)

    
    print("Conectando con el servidor SMTP de Brevo...")

    # Brevo usa smtp-relay.brevo.com con puerto 587 (TLS)
    server = smtplib.SMTP("smtp-relay.brevo.com", 587)
    server.starttls()  # Iniciar conexión segura

    try:
        server.login(EMAIL_EMISOR.strip(), PASSWORD_EMISOR.strip())
        server.sendmail(EMAIL_EMISOR.strip(), EMAIL_KINDLE.strip(), msg.as_string())
        print("[OK] ¡Periódico enviado con éxito a través de Brevo!")
    except Exception as e:
        print(f"[ERROR SMTP]: {e}")
        raise
    finally:
        server.quit()

    if os.path.exists(nombre_archivo):
        os.remove(nombre_archivo)


if __name__ == "__main__":
    try:
        print("Iniciando compilación del periódico...")
        html_data = generar_periodico_html()
        print("Preparando el envío por correo...")
        enviar_a_kindle(html_data)
        print("[OK] Todo el proceso ha finalizado correctamente.")
    except Exception as e:
        print(f"[ERROR GENERAL DEL SCRIPT]: {e}")
        raise
