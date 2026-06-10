import os
import smtplib
import feedparser
import re
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

# URLs corregidas de los feeds RSS
DIARIOS_MEXICO = {
    "La Jornada": "https://www.jornada.com.mx/rss/ultimas.xml",
    "Excélsior": "https://www.excelsior.com.mx/rss",
    "Milenio": "https://www.milenio.com/feed",
}

# Variables de entorno (configuradas en GitHub Secrets)
EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")
PASSWORD_EMISOR = os.environ.get("PASSWORD_EMISOR")
EMAIL_KINDLE = os.environ.get("EMAIL_KINDLE")


def generar_periodico_html():
    html = "<html><head><meta charset='utf-8'></head><body>"
    html += "<h1> Periódico Diario México</h1><hr>"
    html += "<h2>Índice de Secciones</h2><ul>"

    for nombre in DIARIOS_MEXICO.keys():
        id_diario = nombre.replace(" ", "")
        html += f"<li><a href='#{id_diario}'>{nombre}</a></li>"
    html += "</ul><hr>"

    for nombre, url in DIARIOS_MEXICO.items():
        id_diario = nombre.replace(" ", "")
        html += f"<h2 id='{id_diario}'>{nombre}</h2>"

        try:
            print(f"📡 Obteniendo noticias de {nombre}...")
            feed = feedparser.parse(
                url, 
                agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            if not feed.entries:
                print(f" Sin noticias disponibles para {nombre}")
                html += "<p><i>No se pudo cargar este diario hoy.</i></p><hr>"
                continue

            print(f" {len(feed.entries)} noticias encontradas en {nombre}")

            for i, entry in enumerate(feed.entries[:7]):
                titulo = entry.get("title", "Sin título")
                resumen = entry.get("summary", "Sin contenido disponible.")
                # Limpiar HTML del resumen
                resumen_limpio = re.sub('<[^<]+?>', '', resumen)[:300]
                html += f"<h3>{i+1}. {titulo}</h3>"
                html += f"<p>{resumen_limpio}...</p><br>"

            html += "<hr>"
            
        except Exception as e:
            print(f" Error con {nombre}: {e}")
            html += f"<p><i>Error al cargar {nombre}</i></p><hr>"

    html += "</body></html>"
    return html


def enviar_a_kindle(contenido_html):
    if not EMAIL_EMISOR or not PASSWORD_EMISOR or not EMAIL_KINDLE:
        raise ValueError("Faltan configurar variables de entorno en GitHub Secrets.")

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

    # Conexión con Brevo
    print("🔌 Conectando con servidor SMTP de Brevo...")
    server = smtplib.SMTP("smtp-relay.brevo.com", 587)
    server.starttls()

    try:
        # LÍNEA CORRECTA - verifica que estos nombres estén bien escritos
        server.login(EMAIL_EMISOR.strip(), PASSWORD_EMISOR.strip())
        server.sendmail(EMAIL_EMISOR.strip(), EMAIL_KINDLE.strip(), msg.as_string())
        print(" ¡Periódico enviado con éxito a tu Kindle!")
    except Exception as e:
        print(f" ERROR SMTP: {e}")
        raise
    finally:
        server.quit()

    if os.path.exists(nombre_archivo):
        os.remove(nombre_archivo)


if __name__ == "__main__":
    try:
        print(" Iniciando compilación del periódico...")
        html_data = generar_periodico_html()
        print("📧 Preparando el envío por correo...")
        enviar_a_kindle(html_data)
        print(" Todo el proceso ha finalizado correctamente.")
    except Exception as e:
        print(f" ERROR GENERAL DEL SCRIPT: {e}")
        raise
