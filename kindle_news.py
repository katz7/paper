import os
import smtplib
import feedparser
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

# 1. Fuentes RSS estables y verificadas para México
DIARIOS_MEXICO = {
    "La Jornada": "https://jornada.com.mx",
    "Excélsior": "https://excelsior.com.mx",
    "Milenio": "https://milenio.com"
}

# 2. Variables de entorno de GitHub
EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")
PASSWORD_EMISOR = os.environ.get("PASSWORD_EMISOR")
EMAIL_KINDLE = os.environ.get("EMAIL_KINDLE")


def generar_periodico_html():
    html = "<html><head><meta charset='utf-8'></head><body>"
    html += "<h1> Periódico Diario México</h1><hr>"
    html += "<h2>Índice de Secciones</h2><ul>"

    # Generar el índice interactivo para el Kindle
    for nombre in DIARIOS_MEXICO.keys():
        id_diario = nombre.replace(" ", "")
        html += f"<li><a href='#{id_diario}'>{nombre}</a></li>"
    html += "</ul><hr>"

    # Descargar y estructurar noticias
    for nombre, url in DIARIOS_MEXICO.items():
        id_diario = nombre.replace(" ", "")
        html += f"<h2 id='{id_diario}'>{nombre}</h2>"

        # AGENT: Evita bloqueos identificándose como un navegador real
        feed = feedparser.parse(
            url, 
            agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        if feed.bozo:
            print(f"[AVISO] Problema menor al parsear {nombre}, intentando leer de todos modos.")

        if not feed.entries:
            print(f"[ERROR] Sin noticias disponibles para {nombre}")
            html += "<p><i>No se pudo cargar este diario hoy.</i></p><hr>"
            continue

        # Limitar a las 7 noticias principales de cada diario
        for entry in feed.entries[:7]:
            titulo = entry.get("title", "Sin título")
            resumen = entry.get("summary", "Sin contenido disponible.")
            html += f"<h3>{titulo}</h3>"
            html += f"<p>{resumen}</p><br>"

        html += "<hr>"

    html += "</body></html>"
    return html


def enviar_a_kindle(contenido_html):
    if not EMAIL_EMISOR or not PASSWORD_EMISOR or not EMAIL_KINDLE:
        raise ValueError("Error crítico: Faltan configurar variables de entorno en GitHub Secrets.")

    nombre_archivo = "Prensa_Mexico.html"

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(contenido_html)

    # Configuración del paquete del correo electrónico
    msg = MIMEMultipart()
    msg['From'] = EMAIL_EMISOR.strip()
    msg['To'] = EMAIL_KINDLE.strip()
    msg['Subject'] = "Convertir"  # Obligatorio para que Amazon lo procese

    with open(nombre_archivo, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{nombre_archivo}"'
        )
        msg.attach(part)

    print("Conectando de forma segura con el servidor de Gmail...")
    server = smtplib.SMTP_SSL("://gmail.com", 465)

    try:
        # El .strip() limpia espacios invisibles al inicio o final de las contraseñas
        server.login(EMAIL_EMISOR.strip(), PASSWORD_EMISOR.strip())
        server.sendmail(
            EMAIL_EMISOR.strip(),
            EMAIL_KINDLE.strip(),
            msg.as_string()
        )
        print("[OK] ¡Periódico diario enviado exitosamente a tu Kindle!")
    except Exception as e:
        print("[ERROR SMTP]: No se pudo autenticar o enviar el correo.")
        print(f"Detalle técnico: {e}")
        raise
    finally:
        server.quit()

    # Limpieza del archivo temporal local en el servidor de GitHub
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
