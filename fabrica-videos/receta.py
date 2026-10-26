"""Prepara la receta con voz (formato 4): cuadros en cámara lenta del clip real, foto final y tiempos de la voz.

uso: python3 receta.py --clip clip.mp4 --foto rebanada.png --cues '{"p2":3.39,"s2":4.68,...}'
Crea assets/clip2/fNNN.jpg, assets/slice.jpg y receta-voz.html (desde receta-voz.tpl.html).

Claves de --cues (segundos en el video = inicio de la frase de voz.py + retraso de la voz):
  p2     2.ª frase del gancho («…estás perdiendo dinero»)
  s2     escena 2: ingredientes en el molde        n1   número de ingredientes ($14.40)
  p5     comentario corto («Parece poco, ¿verdad?»)
  s3     escena 3: «tu tiempo» (pantalla café)     tiempo  palabra «tu tiempo»   n2  número del trabajo ($22.50)
  s4     escena 4: dividir                         div  «divídelo…» (empiezan los cortes)   n3  costo por porción ($2.75)
  s5     escena 5: foto real + CTA                 cta  «Comenta…»               end  fin de la voz
Los textos y números de la plantilla son los de Mi Repostería: cámbialos en receta-voz.tpl.html para otro postre o marca.
"""
import argparse, json, pathlib, subprocess, shutil
from PIL import Image

here = pathlib.Path(__file__).parent
ap = argparse.ArgumentParser()
ap.add_argument("--clip", required=True); ap.add_argument("--foto", required=True); ap.add_argument("--cues", required=True)
ap.add_argument("--lento", type=float, default=1.7, help="factor de cámara lenta del clip")
a = ap.parse_args()
cues = json.loads(a.cues)
need = ["p2", "s2", "n1", "p5", "s3", "tiempo", "n2", "s4", "div", "n3", "s5", "cta", "end"]
miss = [k for k in need if k not in cues]
if miss: raise SystemExit(f"faltan claves en --cues: {miss}")

d = here / "assets" / "clip2"; shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.clip, "-vf",
                f"setpts={a.lento}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale=720:-2",
                "-q:v", "2", str(d / "f%03d.jpg")], check=True)
Image.open(a.foto).convert("RGB").save(here / "assets" / "slice.jpg", quality=95)
nf = len(list(d.glob("f*.jpg")))
s = (here / "receta-voz.tpl.html").read_text().replace("%%CUES%%", json.dumps(cues)).replace("%%NF%%", str(nf))
(here / "receta-voz.html").write_text(s)
print("ok: receta-voz.html,", nf, "cuadros del clip; duración del video", cues["end"] + 1.2, "s")
