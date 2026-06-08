import os
import smtplib
import feedparser
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

# 1. Configuración de fuentes y credenciales

DIARIOS_MEXICO = {
    "La Jornada": "https://jornada.com.mx",
    "Excélsior": "https://excelsior.com.mx",
    "Milenio": "https://milenio.com.mx"
}



# Configura estas variables en tu entorno o usa un archivo .env

EMAIL_EMISOR = os.getenv("EMAIL_EMISOR")
PASSWORD_EMISOR = os.getenv("PASSWORD_EMISOR")
EMAIL_KINDLE = os.getenv("EMAIL_KINDLE")
``

SMTP_SERVER = "smtp.gmail.com" # Cambiar según tu proveedor
SMTP_PORT = 587

def generar_periodico_html():
    """Descarga los RSS y estructura un HTML limpio."""
    html = "<html><head><meta charset='utf-8'></head><body>"
    html += "<h1>📰 Periódico Diario México</h1><hr>"
    
    # Crear Índice interactivo para el Kindle
    html += "<h2>Índice de Secciones</h2><ul>"
    for nombre in DIARIOS_MEXICO.keys():
        id_diario = nombre.replace(" ", "")
        html += f"<li><a href='#{id_diario}'>{nombre}</a></li>"
    html += "</ul><hr>"
    
    # Descargar y agregar contenido
    for nombre, url in DIARIOS_MEXICO.items():
        id_diario = nombre.replace(" ", "")
        html += f"<h2 id='{id_diario}'>{nombre}</h2>"
        
        feed = feedparser.parse(url)
        # Limitar a las 7 noticias principales por diario
        for entry in feed.entries[:7]:
            titulo = entry.get("title", "Sin título")
            resumen = entry.get("summary", "Sin contenido disponible.")
            html += f"<h3>{titulo}</h3>"
            html += f"<p>{resumen}</p><br>"
        html += "<hr>"
        
    html += "</body></html>"
    return html

def enviar_a_kindle(contenido_html):
    """Genera el archivo adjunto y lo envía vía SMTP."""
    nombre_archivo = "Prensa_Mexico.html"
    
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(contenido_html)
        
    # Configurar el mensaje de correo
    msg = MIMEMultipart()
    msg['From'] = EMAIL_EMISOR
    msg['To'] = EMAIL_KINDLE
    msg['Subject'] = "Convertir"  # Indica a Amazon que procese el archivo
    
    # Adjuntar el archivo HTML
    with open(nombre_archivo, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{nombre_archivo}"')
        msg.attach(part)
        
    # Conexión al servidor de correo
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_EMISOR, PASSWORD_EMISOR)
        server.sendmail(EMAIL_EMISOR, EMAIL_KINDLE, msg.as_string())
        server.quit()
        print("¡Periódico enviado con éxito a tu Kindle!")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    finally:
        if os.path.exists(nombre_archivo):
            os.remove(nombre_archivo)

if __name__ == "__main__":
    print("Descargando noticias de México...")
    html_data = generar_periodico_html()
    print("Enviando a Kindle...")
    enviar_a_kindle(html_data)
