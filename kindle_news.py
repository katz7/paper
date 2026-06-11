import os
import base64
import smtplib
import feedparser
from datetime import datetime
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
    "Proceso economia": "https://www.proceso.com.mx/rss/feed.html?r=2",
    "Proceso Internacional": "https://www.proceso.com.mx/rss/feed.html?r=3",
    "Proceso Ciencia y Tecnología": "https://www.proceso.com.mx/rss/feed.html?r=6",
    "Proceso Cultura": "https://www.proceso.com.mx/rss/feed.html?r=7",
    "Proceso Fotografia": "https://www.proceso.com.mx/rss/feed.html?r=30",
    "Proceso Revista": "https://www.proceso.com.mx/rss/feed.html?r=9"
}
 
EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")
PASSWORD_EMISOR = os.environ.get("PASSWORD_EMISOR")
EMAIL_KINDLE = os.environ.get("EMAIL_KINDLE")
 
 
def imagen_a_base64(ruta):
    try:
        with open(ruta, "rb") as f:
            datos = base64.b64encode(f.read()).decode("utf-8")
        ext = ruta.split(".")[-1].lower()
        mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
        return f"data:image/{mime};base64,{datos}"
    except FileNotFoundError:
        print(f"[AVISO] No se encontró la imagen '{ruta}', se omitirá.")
        return None
 
 
def generar_periodico_html():
    img_base64 = imagen_a_base64("papel.jpeg")
    fecha_hoy = datetime.now().strftime("%A, %d de %B de %Y").capitalize()
 
    css = """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&display=swap');
 
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 
      :root {
        --tinta:      #1a1a1a;
        --papel:      #fdf8f0;
        --rojo:       #c0392b;
        --gris-claro: #d4cfc8;
        --gris-medio: #8a847c;
        --blanco:     #ffffff;
      }
 
      html { font-size: 16px; }
 
      body {
        font-family: 'Source Serif 4', Georgia, serif;
        background-color: var(--papel);
        color: var(--tinta);
        line-height: 1.65;
      }
 
      /* MASTHEAD */
      .masthead {
        border-top: 4px solid var(--tinta);
        border-bottom: 4px solid var(--tinta);
        padding: 16px 40px 12px;
        text-align: center;
      }
      .masthead-meta {
        display: flex;
        justify-content: space-between;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--gris-medio);
        margin-bottom: 8px;
      }
      .masthead h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3.8rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        line-height: 1;
        text-transform: uppercase;
        color: var(--tinta);
      }
      .masthead-rule {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 10px;
      }
      .masthead-rule hr {
        flex: 1;
        border: none;
        border-top: 1px solid var(--tinta);
      }
      .masthead-rule span {
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--gris-medio);
        white-space: nowrap;
      }
      .masthead-img {
        width: 100%;
        max-height: 160px;
        object-fit: cover;
        display: block;
        margin-top: 14px;
        filter: grayscale(30%);
      }
 
      /* LAYOUT */
      .contenedor {
        display: flex;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
      }
 
      /* ÍNDICE LATERAL */
      .indice {
        width: 220px;
        min-width: 220px;
        padding: 28px 20px 28px 0;
        border-right: 1px solid var(--gris-claro);
        position: sticky;
        top: 0;
        height: 100vh;
        overflow-y: auto;
      }
      .indice h2 {
        font-family: 'Playfair Display', serif;
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--rojo);
        border-bottom: 2px solid var(--rojo);
        padding-bottom: 6px;
        margin-bottom: 14px;
      }
      .indice ul { list-style: none; }
      .indice ul li { border-bottom: 1px solid var(--gris-claro); }
      .indice ul li a {
        display: block;
        padding: 7px 4px;
        font-size: 0.82rem;
        color: var(--tinta);
        text-decoration: none;
        transition: color 0.15s, padding-left 0.15s;
      }
      .indice ul li a:hover { color: var(--rojo); padding-left: 8px; }
 
      /* NOTICIAS */
      .noticias {
        flex: 1;
        padding: 28px 0 40px 32px;
      }
 
      .seccion-diario {
        margin-bottom: 52px;
        padding-bottom: 40px;
        border-bottom: 3px double var(--tinta);
      }
      .seccion-diario:last-child { border-bottom: none; }
 
      .seccion-header {
        display: flex;
        align-items: baseline;
        gap: 16px;
        margin-bottom: 20px;
      }
      .seccion-header h2 {
        font-family: 'Playfair Display', serif;
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--tinta);
        line-height: 1.1;
      }
      .etiqueta {
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--blanco);
        background: var(--rojo);
        padding: 3px 8px;
      }
 
      /* GRILLA */
      .articulos-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0;
      }
      .articulo {
        padding: 16px;
        border: 1px solid var(--gris-claro);
        margin: -1px 0 0 -1px;
        background: var(--blanco);
      }
      .articulo:first-child {
        grid-column: 1 / -1;
        background: var(--papel);
        border-top: 3px solid var(--rojo);
      }
      .articulo:hover { background: #faf5eb; }
 
      .articulo h3 {
        font-family: 'Playfair Display', serif;
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.3;
        margin-bottom: 8px;
        color: var(--tinta);
      }
      .articulo:first-child h3 { font-size: 1.35rem; }
      .articulo p {
        font-size: 0.88rem;
        color: #3a3530;
        line-height: 1.6;
        text-align: justify;
      }
 
      .error {
        font-style: italic;
        color: var(--gris-medio);
        font-size: 0.9rem;
        padding: 20px;
        border: 1px dashed var(--gris-claro);
      }
 
      /* RESPONSIVE */
      @media (max-width: 768px) {
        .contenedor { flex-direction: column; }
        .indice {
          width: 100%;
          height: auto;
          position: static;
          border-right: none;
          border-bottom: 2px solid var(--gris-claro);
          padding: 20px 0;
        }
        .noticias { padding: 20px 0; }
        .articulos-grid { grid-template-columns: 1fr; }
        .articulo:first-child { grid-column: 1; }
        .masthead h1 { font-size: 2.4rem; }
      }
 
      /* KINDLE / PRINT */
      @media print {
        .seccion-diario { page-break-after: always; }
        .indice { display: none; }
      }
    </style>
    """
 
    html = f"<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
 
    # Masthead
    html += "<header class='masthead'>"
    html += f"<div class='masthead-meta'><span>{fecha_hoy}</span><span>México · Edición Digital</span><span>Compilación RSS</span></div>"
    html += "<h1>Periódicos CD MX</h1>"
    html += "<div class='masthead-rule'><hr><span>Diarios de México</span><hr></div>"
    if img_base64:
        html += f"<img class='masthead-img' src='{img_base64}' alt='Cabecera'/>"
    html += "</header>"
 
    # Layout
    html += "<div class='contenedor'>"
 
    # Índice lateral
    html += "<nav class='indice'><h2>Secciones</h2><ul>"
    for nombre in DIARIOS_MEXICO.keys():
        id_diario = nombre.replace(" ", "-").lower()
        html += f"<li><a href='#{id_diario}'>{nombre}</a></li>"
    html += "</ul></nav>"
 
    # Artículos
    html += "<main class='noticias'>"
 
    for nombre, url in DIARIOS_MEXICO.items():
        id_diario = nombre.replace(" ", "-").lower()
        fuente = nombre.split()[0]
 
        html += f"<section class='seccion-diario' id='{id_diario}'>"
        html += "<div class='seccion-header'>"
        html += f"<h2>{nombre}</h2><span class='etiqueta'>{fuente}</span>"
        html += "</div>"
 
        feed = feedparser.parse(
            url,
            agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
 
        if not feed.entries:
            print(f"[ERROR] Sin noticias disponibles para {nombre}")
            html += "<p class='error'>No se pudo cargar este diario hoy.</p>"
            html += "</section>"
            continue
 
        html += "<div class='articulos-grid'>"
        for entry in feed.entries[:7]:
            titulo = entry.get("title", "Sin título")
            resumen = entry.get("summary", "")
            html += "<article class='articulo'>"
            html += f"<h3>{titulo}</h3>"
            if resumen:
                html += f"<p>{resumen}</p>"
            html += "</article>"
        html += "</div></section>"
 
    html += "</main></div></body></html>"
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
        part.add_header('Content-Disposition', f'attachment; filename="{nombre_archivo}"')
        msg.attach(part)
 
    print("Conectando con Gmail...")
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
