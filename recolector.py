import requests
from bs4 import BeautifulSoup
from google import genai
import os
import time
import random
import json
from datetime import datetime, timezone

# --- 1. CONFIGURACIÓN DE LA IA ---
API_KEY = os.environ.get("LLAVESECRETABRAI")
client = genai.Client(api_key=API_KEY)

# --- 2. EL RECOLECTOR MULTI-FUENTE ---
fuentes = [
    {"nombre": "ÁMBITO", "url": "https://www.ambito.com/", "base": "https://www.ambito.com"},
    {"nombre": "INFOBAE", "url": "https://www.infobae.com/", "base": "https://www.infobae.com"},
    {"nombre": "TN", "url": "https://tn.com.ar/", "base": "https://tn.com.ar"},
    {"nombre": "IPROFESIONAL", "url": "https://www.iprofesional.com/", "base": "https://www.iprofesional.com"},
    {"nombre": "LA NACION", "url": "https://www.lanacion.com.ar/", "base": "https://www.lanacion.com.ar"}
]

encabezados = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
noticias_extraidas = []
urls_vistas_ronda_actual = set()

palabras_prohibidas = ["javascript", "mailto", "defensa-del-consumidor", "/autor/", "/tema/", "/tags/", "redaccion"]

for fuente in fuentes:
    try:
        respuesta = requests.get(fuente["url"], headers=encabezados, timeout=10)
        if respuesta.status_code == 200:
            sopa = BeautifulSoup(respuesta.text, 'html.parser')
            contador = 0

            articulos = sopa.find_all(['article', 'h1', 'h2', 'h3', 'h4']) 
            for articulo in articulos:
                texto_limpio = " ".join(articulo.text.split())

                if len(texto_limpio) < 20:
                    continue

                enlace_tag = articulo.find('a')
                if not enlace_tag:
                    padres = articulo.find_parents('a')
                    if padres:
                        enlace_tag = padres[0]

                if enlace_tag and 'href' in enlace_tag.attrs:
                    link = enlace_tag['href']

                    if any(prohibido in link.lower() for prohibido in palabras_prohibidas):
                        continue

                    if not link.startswith('http'):
                        if not link.startswith('/'):
                            link = '/' + link
                        link = fuente["base"] + link

                    if link not in urls_vistas_ronda_actual:
                        urls_vistas_ronda_actual.add(link)
                        noticias_extraidas.append({"fuente": fuente["nombre"], "titulo": texto_limpio, "link": link})
                        contador += 1
                        if contador >= 5: 
                            break
    except Exception as e:
        pass

random.shuffle(noticias_extraidas)
noticias_finales = noticias_extraidas[:20] 

# --- MOTOR FORENSE DE EXTRACCIÓN DE HORA ---
print("Extrayendo metadatos de tiempo...")
tiempos_reales = {}

def extraer_fecha_exacta(sopa):
    metas = ['article:published_time', 'article:modified_time', 'datePublished', 'pubdate']
    for m in metas:
        tag = sopa.find('meta', property=m) or sopa.find('meta', itemprop=m) or sopa.find('meta', attrs={'name': m})
        if tag and tag.get('content'):
            return tag['content']

    scripts = sopa.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            if script.string:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'datePublished' in data: return data['datePublished']
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'datePublished' in item:
                            return item['datePublished']
        except:
            pass
    return None

for noticia in noticias_finales:
    link_nota = noticia['link']
    hora_fallback = datetime.now(timezone.utc).isoformat()
    tiempos_reales[link_nota] = hora_fallback 

    try:
        resp_nota = requests.get(link_nota, headers=encabezados, timeout=5)
        if resp_nota.status_code == 200:
            sopa_nota = BeautifulSoup(resp_nota.text, 'html.parser')
            fecha_encontrada = extraer_fecha_exacta(sopa_nota)
            if fecha_encontrada:
                tiempos_reales[link_nota] = fecha_encontrada
    except:
        pass

texto_para_ia = ""
for i, noticia in enumerate(noticias_finales):
    texto_para_ia += f"ID: {i+1} | Diario: {noticia['fuente']} | Título: {noticia['titulo']} | Link: {noticia['link']}\n"

# --- 3. EL SÚPER CEREBRO DE LA IA ---
prompt = f"""
Eres un analista de mercados de alto nivel. Tienes esta lista de noticias:
{texto_para_ia}

TAREAS ESTRICTAS:
1. ELIMINAR CLONES: Si varias noticias hablan de exactamente lo mismo, agrúpalas en una sola. En el campo 'DIARIOS', pon el nombre de todos los medios separados por coma (Ej: INFOBAE, TN).
2. CATEGORÍA: Solo DEPORTES, POLÍTICA, ECONOMÍA o MERCADOS.
3. VIÑETAS & LECTURA ACTIVA: Escribe el resumen en exactamente 3 viñetas cortas, separadas por la etiqueta <br><span class="text-cyan-400 font-bold mr-2">▪</span>. Usa la etiqueta HTML <b>texto</b> para resaltar los datos duros más importantes (cifras, nombres, tickers).
4. CONTEXTO DE IMPACTO: Argumenta de forma concisa y profesional el porqué de la calificación asignada al final de las viñetas (ej. contexto del impacto en la economía local, suba de tasas, etc.).
5. TAGS: 2 o 3 palabras clave separadas por coma.
6. SENTIMIENTO: Evalúa la noticia para el inversor argentino. Responde solo con: POSITIVO, NEGATIVO o NEUTRAL.
7. IMPACTO: Del 1 al 5.

Formato de respuesta estricto separado por el símbolo | :
DIARIOS|CATEGORIA|TÍTULO UNIFICADO|VIÑETAS_HTML|TAGS|SENTIMIENTO|IMPACTO|LINK PRINCIPAL
"""

max_intentos = 3
exito = False
respuesta_ia_texto = ""

for intento in range(max_intentos):
    try:
        respuesta_ia = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        respuesta_ia_texto = respuesta_ia.text
        exito = True
        break
    except Exception as e:
        time.sleep(10)

if not exito:
    try:
        respuesta_ia = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        respuesta_ia_texto = respuesta_ia.text
        exito = True
    except:
        pass

tarjetas_html = ""
noticias_urgentes_ticker = []

if exito:
    lineas = respuesta_ia_texto.strip().split('\n')
    for linea in lineas:
        if "|" in linea:
            partes = linea.split("|")
            if len(partes) >= 8:
                diarios = partes[0].strip().upper()
                categoria = partes[1].strip().upper()
                titulo = partes[2].strip()
                vinetas = partes[3].strip()
                tags_raw = partes[4].strip()
                sentimiento = partes[5].strip().upper()
                impacto = partes[6].strip()
                link = partes[7].strip()

                timestamp_iso = tiempos_reales.get(link, datetime.now(timezone.utc).isoformat())
                try:
                    dt_noticia = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
                    if dt_noticia.tzinfo is None:
                        dt_noticia = dt_noticia.replace(tzinfo=timezone.utc)
                    diferencia_horas = (datetime.now(timezone.utc) - dt_noticia).total_seconds() / 3600
                    if diferencia_horas > 24:
                        continue 
                except:
                    pass

                if impacto == "5" or impacto == "4":
                    noticias_urgentes_ticker.append(titulo)

                if categoria == "MERCADOS":
                    pill = "bg-emerald-900/40 text-emerald-400 border border-emerald-500/30"
                elif categoria == "ECONOMÍA":
                    pill = "bg-blue-900/40 text-blue-400 border border-blue-500/30"
                elif categoria == "DEPORTES":
                    pill = "bg-orange-900/40 text-orange-400 border border-orange-500/30"
                elif categoria == "POLÍTICA":
                    pill = "bg-indigo-900/40 text-indigo-400 border border-indigo-500/30"
                else: 
                    pill = "bg-teal-900/40 text-teal-400 border border-teal-500/30"

                if "POSITIVO" in sentimiento:
                    icono_sent = "🟢"
                    borde_sent = "border-t-4 border-t-emerald-500"
                elif "NEGATIVO" in sentimiento:
                    icono_sent = "🔴"
                    borde_sent = "border-t-4 border-t-rose-500"
                else:
                    icono_sent = "⚪"
                    borde_sent = "border-t-4 border-t-gray-500"

                cantidad_diarios = len(diarios.split(","))
                badge_clon = f'<span class="text-[10px] font-bold bg-yellow-500/20 text-yellow-500 px-2 py-0.5 rounded border border-yellow-500/30 mt-2 inline-block">🗞️ Cubierto por {cantidad_diarios} medios</span>' if cantidad_diarios > 1 else ""

                tags_html = "".join([f'<span class="text-[10px] font-mono bg-gray-800/80 text-cyan-400 px-2 py-1 rounded border border-gray-700">#{t.strip().upper()}</span>' for t in tags_raw.split(",") if t.strip()])

                if not vinetas.startswith('<span'):
                    vinetas = '<span class="text-cyan-400 font-bold mr-2">▪</span>' + vinetas

                tarjetas_html += f"""
                <article data-categoria="{categoria}" data-url="{link}" class="tarjeta-noticia bg-[#0f172a]/70 backdrop-blur-xl rounded-xl p-6 flex flex-col {borde_sent} hover:scale-[1.02] transition-all duration-300 shadow-xl shadow-black/60 border border-gray-800/60 h-[380px] overflow-hidden">
                    <div class="flex justify-between items-start mb-3 shrink-0">
                        <div class="flex flex-col gap-2 max-w-[70%]">
                            <div class="flex flex-wrap gap-2 text-[11px] font-bold tracking-wide">
                                <span class="{pill} px-2 py-1 rounded-md whitespace-nowrap">{categoria}</span>
                                <span class="bg-gray-800/80 text-gray-300 px-2 py-1 rounded-md border border-gray-700 whitespace-nowrap">{icono_sent} {sentimiento}</span>
                            </div>
                            <span class="text-[9px] text-cyan-400 font-black font-mono tracking-wide uppercase break-all">{diarios}</span>
                        </div>
                        <div class="flex flex-col items-end gap-1 shrink-0">
                            <span class="tiempo-noticia text-gray-400 text-xs font-mono bg-gray-900/80 border border-gray-700 px-2
