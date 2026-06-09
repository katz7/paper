import os
import smtplib
import feedparser
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders


#  Fuentes RSS válidas
DIARIOS_MEXICO = {
    "El Universal": "https://www.eluniversal.com.mx/rss.xml",
    "Milenio": "https://www.milenio.com/rss",
    "Animal Político": "https://www.animalpolitico.com/feed/"
}

# Variables de entorno (SIEMPRE arriba)
EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")
PASSWORD_EMISOR = os.environ.get("PASSWORD_EMISOR")
EMAIL_KINDLE = os.environ.get("EMAIL_KINDLE")

#  Debug (puedes quitar luego)
print("EMAIL:", EMAIL_EMISOR)
print("PASS LENGTH:", len(PASSWORD_EMISOR) if PASSWORD_EMISOR else 0)


def generar_periodico_html():
    html = "<html><head><meta charset='utf-8'></head><body>"
    html += "<h1>Periódico Diario México</h1><hr>"
    html += "<h2>Índice</h2><ul>"

    for nombre in DIARIOS_MEXICO.keys():
        id_diario = nombre.replace(" ", "")
        html += f"<li><a href='#{id_diario}'>{nombre}</a></li>"
    html += "</ul><hr>"

    for nombre, url in DIARIOS_MEXICO.items():
        id_diario = nombre.replace(" ", "")
        html += f"<h2 id='{id_diario}'>{nombre}</h2>"

        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"[ERROR] No se pudo leer {nombre}: {feed.bozo_exception}")
            html += "<p><i>No se pudo cargar este diario hoy.</i></p><hr>"
            continue

        if not feed.entries:
            print(f"[AVISO] Sin entradas para {nombre}")
            html += "<p><i>Sin noticias disponibles.</i></p><hr>"
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
    if not EMAIL_EMISOR or not PASSWORD_EMISOR or not EMAIL_KINDLE:
        raise ValueError("Faltan variables de entorno")

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
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{nombre_archivo}"'
        )
        msg.attach(part)

    #  SMTP corregido (esto era CLAVE)
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    try:
        server.login(EMAIL_EMISOR.strip(), PASSWORD_EMISOR.strip())
        server.sendmail(
            EMAIL_EMISOR,
            EMAIL_KINDLE,
            msg.as_string()
        )
        print("[OK] Correo enviado a Kindle")
    except Exception as e:
        print("[ERROR SMTP]", e)
        raise
    finally:
        server.quit()

    os.remove(nombre_archivo)


if __name__ == "__main__":
    try:
        print("Generando periódico...")
        html_data = generar_periodico_html()

        print("Enviando a Kindle...")
        enviar_a_kindle(html_data)

        print("[OK] Proceso completado")
    except Exception as e:
        print(f"[ERROR GENERAL]: {e}")
        raise
