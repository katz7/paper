import os
import smtplib
import feedparser
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

DIARIOS_MEXICO = {
    "La Jornada": "https://www.jornada.com.mx/ultimas/rss.xml",
    "Excélsior": "https://www.excelsior.com.mx/rss.xml",
    "Milenio": "https://www.milenio.com/rss",
    "El Universal": "https://www.eluniversal.com.mx/rss.xml",
    "Reforma": "https://www.reforma.com/rss/portada.xml",
}

EMAIL_EMISOR = os.getenv("EMAIL_EMISOR")
PASSWORD_EMISOR = os.getenv("PASSWORD_EMISOR")
EMAIL_KINDLE = os.getenv("EMAIL_KINDLE")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def generar_periodico_html():
    html = "<html><head><meta charset='utf-8'></head><body>"
    html += "<h1>📰 Periódico Diario México</h1><hr>"
    html += "<h2>Índice</h2><ul>"

    for nombre in DIARIOS_MEXICO.keys():
        id_diario = nombre.replace(" ", "")
        html += f"<li><a href='#{id_diario}'>{nombre}</a></li>"
    html += "</ul><hr>"

    for nombre, url in DIARIOS_MEXICO.items():
        id_diario = nombre.replace(" ", "")
        html += f"<h2 id='{id_diario}'>{nombre}</h2>"

        feed = feedparser.parse(url)

        # ✅ NUEVO: validar si el feed falló
        if feed.bozo:
            print(f"⚠️  Error al leer {nombre}: {feed.bozo_exception}")
            html += f"<p><i>No se pudo cargar este diario hoy.</i></p><hr>"
            continue

        if not feed.entries:
            print(f"⚠️  Sin entradas para {nombre}")
            html += f"<p><i>Sin noticias disponibles.</i></p><hr>"
            continue

        for entry in feed.entries[:7]:
            titulo = entry.get("title", "Sin título")
            resumen = entry.get("summary", "Sin contenido")
            html += f"<h3>{titulo}</h3>"
            html += f"<p>{resumen}</p><br>"
        html += "<hr>"

    html += "</body></html>"
    return html


def enviar_a_kindle(contenido_html):
    # ✅ NUEVO: validar que los secrets existen antes de intentar enviar
    if not EMAIL_EMISOR or not PASSWORD_EMISOR or not EMAIL_KINDLE:
        raise ValueError("❌ Faltan variables de entorno: EMAIL_EMISOR, PASSWORD_EMISOR o EMAIL_KINDLE")

    nombre_archivo = "Prensa_Mexico.html"

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(contenido_html)

    msg = MIMEMultipart()
    msg['From'] = EMAIL_EMISOR
    msg['To'] = EMAIL_KINDLE
    msg['Subject'] = "Convertir"

    with open(nombre_archivo, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{nombre_archivo}"')
        msg.attach(part)

    # ✅ NUEVO: cerrar conexión segura aunque falle
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    try:
        server.starttls()
        server.login(EMAIL_EMISOR, PASSWORD_EMISOR)
        server.sendmail(EMAIL_EMISOR, EMAIL_KINDLE, msg.as_string())
        print("✅ Correo enviado correctamente a Kindle")
    finally:
        server.quit()

    # ✅ NUEVO: limpiar archivo temporal
    os.remove(nombre_archivo)


if __name__ == "__main__":
    try:
        html_data = generar_periodico_html()
        enviar_a_kindle(html_data)
        print("✅ Periódico enviado correctamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise  # hace que el Action de GitHub marque el job como fallido y te notifica
