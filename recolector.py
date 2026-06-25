import json
import os
from datetime import datetime

# 1. LÓGICA DE RECOLECCIÓN Y PROCESAMIENTO
# Aquí deberías conectar tu lógica real de scraping y cálculo.
# Simulamos los datos para que puedas probar la máquina ya mismo.

# Simulamos la lectura de clones/historial desde tu historial.txt
total_filtradas_hoy = 142
clones_bloqueados_hoy = 18

datos_mercado = {
    "backend": {
        "estado": "Online",
        "sincro": f"Actualizado: {datetime.now().strftime('%H:%M:%S')}",
        "total_filtradas": total_filtradas_hoy,
        "clones_bloqueados": clones_bloqueados_hoy
    },
    "mercado_superior": {
        "oficial": "945,50", "blue": "1245,00", "blue_brecha": "31.6%",
        "mep": "1215,20", "ccl": "1238,40",
        "riesgo_pais": "1.342", "riesgo_pais_pb": "-24 pb", "riesgo_pais_var": "-1.75%"
    },
    "commodities": [
        {"ticker": "BZ=F", "nombre": "Crudo Brent", "valor": "82,45", "variacion": "+1.12%", "pos": True},
        {"ticker": "GC=F", "nombre": "Oro", "valor": "2.345,10", "variacion": "-0.34%", "pos": False},
        {"ticker": "ZS=F", "nombre": "Soja", "valor": "432,25", "variacion": "+0.85%", "pos": True},
        {"ticker": "DX-Y", "nombre": "Índice Dólar", "valor": "104,20", "variacion": "-0.12%", "pos": False}
    ],
    "noticias": [
        {"id": 1, "titulo": "URGENTE: La Fed mantiene las tasas de interés sin cambios", "resumen": "▪ El comité resolvió **congelar la tasa**. Mercados reaccionan con selectividad.", "urgencia": "critico"},
        {"id": 2, "titulo": "ATENCIÓN: Caputo anuncia nuevas metas fiscales", "resumen": "▪ Se busca **acelerar el superávit primario**. Impacto en bonos soberanos.", "urgencia": "critico"},
        {"id": 3, "titulo": "Pampa Energía incrementará inversión en Vaca Muerta", "resumen": "▪ Inyección de **capital estratégico** para elevar extracción de gas natural.", "urgencia": "reciente"},
        {"id": 4, "titulo": "Balance trimestral de Aluar supera las expectativas", "resumen": "▪ Ingresos netos firmes respaldados por la **demanda exterior**.", "urgencia": "normal"}
    ]
}

# Convertimos los datos a formato JSON para inyectarlos en JS
json_data = json.dumps(datos_mercado)

# 2. GENERACIÓN DEL HTML (El Python escribe el archivo)
html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terminal de Mercados</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .font-mono-terminal {{ font-family: 'JetBrains Mono', monospace; }}
        @keyframes pulse-fast {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
        .animate-pulse-fast {{ animation: pulse-fast 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite; }}
    </style>
</head>
<body class="bg-[#121212] text-[#E0E0E0] min-h-screen flex flex-col justify-between select-none">

    <header class="w-full bg-[#1A1A1A] border-b border-[#2A2A2A] px-4 py-2 flex items-center justify-between sticky top-0 z-50">
        <div class="flex space-x-6 items-center">
            <div class="flex flex-col"><span class="text-xs text-gray-400 font-semibold">OFICIAL</span><span id="p-oficial" class="font-mono-terminal text-sm font-bold text-white">---</span></div>
            <div class="flex flex-col"><span class="text-xs text-gray-400 font-semibold">BLUE</span>
                <div class="flex items-center space-x-1"><span id="p-blue" class="font-mono-terminal text-sm font-bold text-white">---</span><span id="p-brecha" class="font-mono-terminal text-xs text-[#00E5FF] font-medium">---</span></div>
            </div>
            <div class="flex flex-col"><span class="text-xs text-gray-400 font-semibold">MEP</span><span id="p-mep" class="font-mono-terminal text-sm font-bold text-white">---</span></div>
            <div class="flex flex-col"><span class="text-xs text-gray-400 font-semibold">CCL</span><span id="p-ccl" class="font-mono-terminal text-sm font-bold text-white">---</span></div>
        </div>
        <div class="flex flex-col items-end">
            <span class="text-xs text-gray-400 font-semibold flex items-center gap-1">RIESGO PAÍS <span class="text-[10px]">🇦R</span></span>
            <div class="flex items-center space-x-2">
                <span id="p-rp-valor" class="font-mono-terminal text-base font-bold text-white">---</span>
                <span id="p-rp-var" class="font-mono-terminal text-xs px-1.5 py-0.5 rounded bg-[#1A3A2A] text-[#00E5FF] font-medium">---</span>
            </div>
        </div>
    </header>

    <div class="flex flex-1 w-full">
        <aside class="w-64 bg-[#161616] border-r border-[#2A2A2A] p-4 flex flex-col justify-between">
            <div class="space-y-6">
                <div>
                    <div id="reloj-art" class="font-mono-terminal text-xl font-bold text-white">00:00:00</div>
                    <div class="text-xs text-gray-400 mt-0.5 flex items-center gap-1.5">
                        <span id="mercado-status-dot" class="w-2 h-2 rounded-full"></span> Mercado: 11 a 17hs
                    </div>
                </div>
                <hr class="border-[#2A2A2A]">
                <div class="space-y-2">
                    <h3 class="text-xs font-bold text-gray-400 tracking-wider uppercase">Backend Actions</h3>
                    <div class="bg-[#1A1A1A] p-2.5 rounded border border-[#232323] text-xs space-y-1.5">
                        <div class="flex justify-between items-center"><span class="text-gray-400">Estado:</span><span class="text-[#00E5FF] font-semibold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-[#00E5FF] animate-pulse-fast"></span> OK</span></div>
                        <div class="flex justify-between"><span class="text-gray-400">Ejecución:</span><span id="meta-sincro" class="font-mono-terminal text-gray-300">---</span></div>
                        <div class="flex justify-between"><span class="text-gray-400">Filtro hoy:</span><span class="font-mono-terminal text-gray-300"><span id="meta-filtradas">---</span> / <span id="meta-clones" class="text-red-400">---</span></span></div>
                    </div>
                </div>
                <div class="space-y-2">
                    <h3 class="text-xs font-bold text-gray-400 tracking-wider uppercase">Monitor Global</h3>
                    <div id="contenedor-commodities" class="bg-[#1A1A1A] p-2.5 rounded border border-[#232323] space-y-2.5 text-xs"></div>
                </div>
            </div>
            <div class="space-y-2 pt-4 border-t border-[#2A2A2A]">
                <button id="btn-toggle-vista" onclick="alternarVista()" class="w-full text-left text-xs bg-[#222] hover:bg-[#2A2A2A] text-gray-300 py-2 px-3 rounded font-medium border border-[#333] transition-all cursor-pointer">👁️ Ver Listado Leídas</button>
                <button onclick="resetearHistorial()" class="w-full text-left text-xs bg-[#2D1F1F] hover:bg-[#3D2525] text-red-300 py-1.5 px-3 rounded font-medium transition-all cursor-pointer">🗑️ Resetear Historial</button>
            </div>
        </aside>

        <main class="flex-1 p-6 overflow-y-auto">
            <h2 id="titulo-seccion" class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Noticias de Mercados</h2>
            <div id="contenedor-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
        </main>
    </div>

    <footer class="w-full bg-[#1A1A1A] border-t border-[#2A2A2A] px-6 py-3 flex justify-between items-center text-xs text-gray-500">
        <div>Terminal v2.5 • <span class="font-mono-terminal">2026</span></div>
        <a href="https://www.linkedin.com/in/brian-yapura-061522156/" target="_blank" class="bg-[#222] hover:bg-[#2A2A2A] text-gray-300 px-3 py-1.5 rounded border border-[#333] transition-all">Conocé mi Perfil Profesional</a>
    </footer>

    <script>
        // INYECCIÓN DIRECTA DE DATOS DESDE PYTHON A JS
        const terminalData = {json_data};
        
        let vistaActual = "principales";

        function actualizarReloj() {{
            const ahora = new Date();
            const opciones = {{ timeZone: 'America/Argentina/Buenos_Aires', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }};
            document.getElementById('reloj-art').innerText = ahora.toLocaleTimeString('es-AR', opciones);
            const h = ahora.getHours();
            document.getElementById('mercado-status-dot').className = (h >= 11 && h < 17) ? "w-2 h-2 rounded-full bg-emerald-500" : "w-2 h-2 rounded-full bg-red-500";
        }}
        setInterval(actualizarReloj, 1000); actualizarReloj();

        function inicializarDatos() {{
            document.getElementById('p-oficial').innerText = terminalData.mercado_superior.oficial;
            document.getElementById('p-blue').innerText = terminalData.mercado_superior.blue;
            document.getElementById('p-brecha').innerText = `(Brecha: ${{terminalData.mercado_superior.blue_brecha}} ↑)`;
            document.getElementById('p-mep').innerText = terminalData.mercado_superior.mep;
            document.getElementById('p-ccl').innerText = terminalData.mercado_superior.ccl;
            document.getElementById('p-rp-valor').innerText = terminalData.mercado_superior.riesgo_pais;
            document.getElementById('p-rp-var').innerText = `${{terminalData.mercado_superior.riesgo_pais_pb}} (${{terminalData.mercado_superior.riesgo_pais_var}})`;

            document.getElementById('meta-sincro').innerText = terminalData.backend.sincro;
            document.getElementById('meta-filtradas').innerText = terminalData.backend.total_filtradas;
            document.getElementById('meta-clones').innerText = terminalData.backend.clones_bloqueados;

            const boxComm = document.getElementById('contenedor-commodities');
            boxComm.innerHTML = terminalData.commodities.map(c => `
                <div class="flex justify-between items-center">
                    <span class="text-gray-300 font-medium">${{c.ticker}}</span>
                    <div class="text-right">
                        <span class="font-mono-terminal text-white font-bold block">${{c.valor}}</span>
                        <span class="font-mono-terminal text-[11px] ${{c.pos ? 'text-[#00E5FF]' : 'text-red-400'}}">${{c.variacion}}</span>
                    </div>
                </div>
            `).join('');
            
            renderizarNoticias();
        }}

        function renderizarNoticias() {{
            const grid = document.getElementById('contenedor-grid');
            grid.innerHTML = "";
            const leidos = JSON.parse(localStorage.getItem('noticias_leidas')) || [];
            
            const filtradas = terminalData.noticias.filter(n => vistaActual === "principales" ? !leidos.includes(n.id) : leidos.includes(n.id));

            if(filtradas.length === 0) {{
                grid.innerHTML = `<p class="text-gray-500 text-xs italic col-span-full py-4 text-center">No hay noticias aquí.</p>`;
                return;
            }}

            filtradas.forEach(noticia => {{
                let borderClass = "border-[#2A2A2A]";
                let badgeHTML = "";

                if (vistaActual === "principales") {{
                    if (noticia.urgencia === "critico") {{ borderClass = "border-l-4 border-l-red-500 border-t-[#2A2A2A] border-r-[#2A2A2A] border-b-[#2A2A2A]"; badgeHTML = `<span class="bg-red-950 text-red-400 text-[10px] font-bold px-1.5 py-0.5 rounded tracking-wide uppercase">URGENTE</span>`; }}
                    else if (noticia.urgencia === "reciente") {{ borderClass = "border-l-4 border-l-amber-500 border-t-[#2A2A2A] border-r-[#2A2A2A] border-b-[#2A2A2A]"; badgeHTML = `<span class="bg-amber-950 text-amber-400 text-[10px] font-bold px-1.5 py-0.5 rounded tracking-wide uppercase">NUEVO</span>`; }}
                }} else {{
                    badgeHTML = `<span class="bg-zinc-800 text-zinc-400 text-[10px] font-bold px-1.5 py-0.5 rounded tracking-wide">LEÍDA</span>`;
                }}

                const card = document.createElement('div');
                card.className = `bg-[#1A1A1A] border ${{borderClass}} rounded p-4 h-[380px] flex flex-col justify-between transition-all duration-300 relative ${{vistaActual === "leidas" ? "opacity-70" : ""}}`;
                card.innerHTML = `
                    <div class="space-y-3 overflow-hidden">
                        <div class="flex items-center justify-between gap-2">${{badgeHTML}}<span class="text-[11px] text-gray-500 font-mono-terminal">ID: #${{noticia.id}}</span></div>
                        <h3 class="text-white font-semibold text-sm leading-snug line-clamp-3">${{noticia.titulo}}</h3>
                        <p class="text-gray-400 text-xs leading-relaxed line-clamp-6">${{noticia.resumen}}</p>
                    </div>
                    <div class="pt-2 border-t border-[#232323] flex justify-end">
                        ${{vistaActual === 'principales' 
                            ? `<button onclick="marcarComoLeida(${{noticia.id}}, this)" class="text-xs text-[#00E5FF] hover:underline font-medium cursor-pointer">Marcar como leída</button>`
                            : `<span class="text-xs text-gray-500 italic">Consumida</span>`
                        }}
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        function marcarComoLeida(id, boton) {{
            const tarjeta = boton.closest('.relative');
            tarjeta.style.opacity = "0"; tarjeta.style.transform = "scale(0.95)";
            setTimeout(() => {{
                let leidos = JSON.parse(localStorage.getItem('noticias_leidas')) || [];
                if (!leidos.includes(id)) {{ leidos.push(id); localStorage.setItem('noticias_leidas', JSON.stringify(leidos)); }}
                renderizarNoticias();
            }}, 300);
        }}

        function alternarVista() {{
            vistaActual = vistaActual === "principales" ? "leidas" : "principales";
            document.getElementById('btn-toggle-vista').innerText = vistaActual === "principales" ? "👁️ Ver Listado Leídas" : "👁️ Ver Principales";
            document.getElementById('titulo-seccion').innerText = vistaActual === "principales" ? "Noticias de Mercados" : "Historial de Noticias Leídas";
            renderizarNoticias();
        }}

        function resetearHistorial() {{
            localStorage.removeItem('noticias_leidas');
            vistaActual = "principales";
            document.getElementById('btn-toggle-vista').innerText = "👁️ Ver Listado Leídas";
            document.getElementById('titulo-seccion').innerText = "Noticias de Mercados";
            renderizarNoticias();
        }}

        window.onload = inicializarDatos;
    </script>
</body>
</html>
"""

# 3. GUARDAMOS EL ARCHIVO PARA QUE GITHUB ACTIONS LO DETECTE
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Archivo index.html generado con éxito.")
