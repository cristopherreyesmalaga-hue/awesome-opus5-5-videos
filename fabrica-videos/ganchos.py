"""Crea variantes de un video que solo cambian el gancho (los primeros 3 s), para probar cuál detiene más el scroll.

uso: python3 ganchos.py video.html ganchos.json
ganchos.json:
  [
    {"nombre": "pregunta",   "reemplazos": [["¿Tu tres leches", "¿Cuánto ganas"], ["te deja ganancia", "por cada"], ["o solo trabajo?", "rebanada?"]]},
    {"nombre": "contraste",  "reemplazos": [["…texto original…", "…texto nuevo…"]]}
  ]
Cada reemplazo es [texto exacto del HTML, texto nuevo] y debe aparecer UNA sola vez en el archivo.
Mantén el mismo número de líneas del gancho (cada línea tiene su propia animación) y largos parecidos.
Escribe <video>-g1-<nombre>.html, <video>-g2-<nombre>.html…; después renderiza cada uno con render.py.
Las variantes de la receta con voz también necesitan su propia 1.ª parte de voz (una generación por gancho).
"""
import sys, json, pathlib, re, unicodedata

src, spec = pathlib.Path(sys.argv[1]), json.loads(pathlib.Path(sys.argv[2]).read_text())
base = src.read_text()
variantes = []
for n, g in enumerate(spec, 1):
    s = base
    for viejo, nuevo in g["reemplazos"]:
        k = s.count(viejo)
        if k != 1:
            raise SystemExit(f"gancho {n} ({g['nombre']}): «{viejo}» aparece {k} veces en {src.name}; usa un texto más largo y único")
        s = s.replace(viejo, nuevo)
    plano = unicodedata.normalize("NFKD", g["nombre"]).encode("ascii", "ignore").decode().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", plano).strip("-") or "v"
    variantes.append((src.with_name(f"{src.stem}-g{n}-{slug}.html"), s))
for out, s in variantes:  # se escriben solo si todas las variantes son válidas
    out.write_text(s); print(out.name)
