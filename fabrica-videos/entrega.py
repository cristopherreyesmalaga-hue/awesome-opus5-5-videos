"""Arma la página de entrega (ver y descargar los videos desde el celular o el iPad, con la descripción del Reel lista para copiar).

uso: python3 entrega.py entrega.json carpeta_salida
entrega.json:
  {
    "titulo": "Videos Mi Repostería", "kicker": "Lote del 26 oct 2026", "meta": "4 videos 9:16 · listos para Reels y TikTok",
    "colores": {"fondo": "#FCF6EC", "tarjeta": "#FFFDFA", "tinta": "#41261A", "suave": "#7A6357", "borde": "#EBDBCE", "acento": "#AF4C60"},
    "videos": [
      {"archivo": "out/Receta.mp4", "titulo": "Receta con voz", "etapa": "Orgánico que vende",
       "uso": "Publícalo como Reel con su audio.", "descripcion": "Texto del Reel…"}
    ]
  }
Copia cada MP4 a la carpeta de salida con un nombre sin espacios ni acentos y escribe index.html.
Publícala con la herramienta Artifact: file_path = carpeta/index.html, files = {nombre.mp4: carpeta/nombre.mp4},
capabilities = {"downloads": true}. Cada MP4 debe pesar menos de 15 MB (si no, vuelve a codificar con -crf 21).
"""
import sys, json, pathlib, shutil, re, unicodedata, html

here = pathlib.Path(__file__).parent
spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
dest = pathlib.Path(sys.argv[2]); dest.mkdir(parents=True, exist_ok=True)
c = {"fondo": "#FCF6EC", "tarjeta": "#FFFDFA", "tinta": "#41261A", "suave": "#7A6357", "borde": "#EBDBCE", "acento": "#AF4C60"}
c.update(spec.get("colores", {}))

def limpio(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9.-]+", "-", s).strip("-")

datos, archivos = [], []
for v in spec["videos"]:
    src = pathlib.Path(v["archivo"]); nombre = limpio(src.name)
    mb = src.stat().st_size / 1e6
    if mb > 14.5:
        raise SystemExit(f"{src.name} pesa {mb:.1f} MB: vuelve a codificarlo (ffmpeg -crf 21) para que quede bajo 15 MB")
    shutil.copy(src, dest / nombre); archivos.append(nombre)
    datos.append({**v, "archivo": nombre})

s = (here / "entrega" / "pagina.html").read_text()
for k, val in {"TITULO": spec["titulo"], "KICKER": spec.get("kicker", ""), "META": spec.get("meta", "")}.items():
    s = s.replace(f"%%{k}%%", html.escape(val))
for k in ["fondo", "tarjeta", "tinta", "suave", "borde", "acento"]:
    s = s.replace(f"%%{k.upper()}%%", c[k])
s = s.replace("%%DATOS%%", json.dumps(datos, ensure_ascii=False).replace("</", "<\\/"))
(dest / "index.html").write_text(s)
print(json.dumps({"pagina": str(dest / "index.html"), "files": {n: str(dest / n) for n in archivos}}, ensure_ascii=False))
