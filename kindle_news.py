import os
import smtplib
import feedparser
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

DIARIOS_MEXICO = {
    "La Jornada": "https://www.jornada.com.mx/rss/edicion.xml?v=1",
    "Reforma": "https://www.reforma.com/rss/portada.xml",
    "Reforma ciudad": "https://www.reforma.com/rss/ciudad.xml",
    "Reforma justicia": "https://www.reforma.com/rss/justicia.xml",
    "Reforma internacional": "https://www.reforma.com/rss/internacional.xml", 
    "Reforma cultura": "https://www.reforma.com/rss/cultura.xml",
    "Reforma gadgets": "https://www.reforma.com/rss/gadgets.xml",
    "Proceso nacional": "https://www.proceso.com.mx/rss/feed.html?r=1",
    "Proceso economina": "https://www.proceso.com.mx/rss/feed.html?r=2",
    "Proceso Internacional": "https://www.proceso.com.mx/rss/feed.html?r=3",
    "Proceso Ciencia y Tecnología": "https://www.proceso.com.mx/rss/feed.html?r=6",
    "Proceso Cultura": "https://www.proceso.com.mx/rss/feed.html?r=7",
    "Proceso Fotografia": "https://www.proceso.com.mx/rss/feed.html?r=30",
    "preceso Revista": "https://www.proceso.com.mx/rss/feed.html?r=9"
    #  "Excélsior": "https://www.excelsior.com.mx/rss/",
   # "El universal": "https://archivo.eluniversal.com.mx/disenio/servicios/EU_rss.htm",
    #"milenio": "https://www.milenio.com/api/v1/rss"
}

EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")
PASSWORD_EMISOR = os.environ.get("PASSWORD_EMISOR")
EMAIL_KINDLE = os.environ.get("EMAIL_KINDLE")


def generar_periodico_html():
    # Estilos CSS optimizados para tinta electrónica (Kindle)
    css_kindle = """
    <style>
        body {
            font-family: Georgia, serif;
            color: #000000;
            background-color: #ffffff;
            line-height: 1.5;
            margin: 5%;
            padding: 0;
        }
        h1 {
            font-size: 2.2em;
            text-align: center;
            text-transform: uppercase;
            border-bottom: 3px double #000000;
            padding-bottom: 10px;
            margin-top: 0;
        }
        h2 {
            font-size: 1.6em;
            border-bottom: 1px solid #000000;
            padding-bottom: 5px;
            margin-top: 1.5em;
        }
        h3 {
            font-size: 1.2em;
            margin-top: 1.2em;
            margin-bottom: 0.3em;
            line-height: 1.3;
        }
        p {
            font-size: 1em;
            margin-top: 0;
            margin-bottom: 1.5em;
            text-align: justify;
        }
        ul {
            list-style-type: square;
            padding-left: 20px;
        }
        li {
            margin-bottom: 8px;
        }
        a {
            color: #000000;
            text-decoration: underline;
        }
        .indice {
            margin-bottom: 2em;
        }
        /* Crucial para Kindle: Fuerza a cada periódico a iniciar en una nueva pantalla */
        .seccion-diario {
            page-break-after: always;
        }
        .error {
            font-style: italic;
            color: #555555;
        }
    </style>
    """

    # Inicio del documento con codificación y estilos
    html = f"<html><head><meta charset='utf-8'>{css_kindle}</head><body>"
    
    # Encabezado principal
    html += "<h1>Periódico de México</h1>"
    
    # Índice de secciones
    html += "<div class='indice'>"
    html += "<h2>Índice de Secciones</h2>"
    html += "<ul>"
    for nombre in DIARIOS_MEXICO.keys():
        id_diario = nombre.replace(" ", "")
        html += f"<li><a href='#{id_diario}'>{nombre}</a></li>"
    html += "</ul>"
    html += "</div>"
    
    # Salto de página para que el primer diario no empiece pegado al índice
    html += "<div style='page-break-after: always;'></div>"

    # Contenido de los diarios
    for nombre, url in DIARIOS_MEXICO.items():
        id_diario = nombre.replace(" ", "")
        
        # Envolvemos cada diario en un contenedor de sección
        html += f"<div class='seccion-diario'>"
        html += f"<h2 id='{id_diario}'>{nombre}</h2>"

        feed = feedparser.parse(
            url, 
            agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        if not feed.entries:
            print(f"[ERROR] Sin noticias disponibles para {nombre}")
            html += "<p class='error'>No se pudo cargar este diario hoy.</p>"
            html += "</div>" # Cierre de seccion-diario
            continue

        for entry in feed.entries[:7]:
            titulo = entry.get("title", "Sin título")
            resumen = entry.get("summary", "Sin contenido disponible.")
            
            # Limpieza básica por si el resumen trae HTML sucio
            # (El Kindle lee mejor el texto plano en los párrafos)
            html += f"<h3>{titulo}</h3>"
            html += f"<p>{resumen}</p>"

        html += "</div>" # Cierre de seccion-diario

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

    print("Conectando de forma segura con el servidor de Gmail...")
    
    # Dirección limpia corregida
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    try:
        server.login(EMAIL_EMISOR.strip(), PASSWORD_EMISOR.strip())
        server.sendmail(EMAIL_EMISOR.strip(), EMAIL_KINDLE.strip(), msg.as_string())
        print("[OK] ¡Periódico enviado con éxito!")
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
