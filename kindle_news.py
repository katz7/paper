import os
import smtplib
import feedparser
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

DIARIOS_MEXICO = {
    "La Jornada": "https://www.jornada.com.mx/rss",
    "Excélsior": "https://www.excelsior.com.mx/rss.xml",
    "Milenio": "https://www.milenio.com/rss"
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
        for entry in feed.entries[:7]:
            titulo = entry.get("title", "Sin título")
            resumen = entry.get("summary", "Sin contenido")
            html += f"<h3>{titulo}</h3>"
            html += f"<p>{resumen}</p><br>"

        html += "<hr>"

    html += "</body></html>"
    return html

def enviar_a_kindle(contenido_html):
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

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_EMISOR, PASSWORD_EMISOR)
    server.sendmail(EMAIL_EMISOR, EMAIL_KINDLE, msg.as_string())
    server.quit()

if __name__ == "__main__":
    html_data = generar_periodico_html()
    enviar_a_kindle(html_data)
``
