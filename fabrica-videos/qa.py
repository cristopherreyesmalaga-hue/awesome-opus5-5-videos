"""Control de calidad de un MP4 vertical antes de entregarlo.

uso: python3 qa.py video.mp4 [--cada 1.0] [--tiempos 0,2.5,7] [--hoja hoja.jpg]
Revisa:
  1. Hoja de cuadros con la ZONA SEGURA de Reels marcada (x 0–930, y 220–1500): nada importante fuera del recuadro azul.
  2. Saltos de imagen de un solo cuadro (diferencia 3 veces mayor que sus vecinos): deben ser 0,
     salvo cortes planeados (p. ej. 3.0 y 6.0 s en el híbrido, donde cambian los clips del avatar).
  3. Volumen integrado (debe estar cerca de -14 LUFS) y duración.
Mira SIEMPRE la hoja con la herramienta Read antes de entregar.
"""
import argparse, subprocess, re, io
import numpy as np
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--cada", type=float, default=1.0); ap.add_argument("--tiempos")
ap.add_argument("--hoja", default=None)
a = ap.parse_args()
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video], capture_output=True, text=True).stdout)
ts = [float(x) for x in a.tiempos.split(",")] if a.tiempos else list(np.arange(0, dur - 0.05, a.cada))

W, H, cols = 270, 480, 8
rows = (len(ts) + cols - 1) // cols
hoja = Image.new("RGB", (cols * W, rows * (H + 24)), "white"); dr = ImageDraw.Draw(hoja)
for n, t in enumerate(ts):
    png = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", a.video, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    im = Image.open(io.BytesIO(png)).convert("RGB"); d = ImageDraw.Draw(im)
    d.rectangle([0, 220, 930, 1500], outline=(0, 190, 255), width=5)
    x, y = (n % cols) * W, (n // cols) * (H + 24)
    hoja.paste(im.resize((W, H)), (x, y + 24)); dr.text((x + 4, y + 5), f"{t:.2f}s", fill="black")
salida = a.hoja or a.video.rsplit(".", 1)[0] + "-qa.jpg"
hoja.save(salida, quality=85)

raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.video, "-vf", "scale=108:192,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, 192, 108).astype(float)
d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
saltos = [round((i + 1) / 30, 2) for i in range(1, len(d) - 1) if d[i] > 3 * max(d[i - 1], d[i + 1], 0.8) and d[i] > 4]
r = subprocess.run(["ffmpeg", "-nostats", "-i", a.video, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
lu = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
print(f"hoja: {salida}\nduracion: {dur:.2f} s\nsaltos de imagen: {saltos or 'ninguno'}\naudio: {lu[-1] + ' LUFS' if lu else 'sin audio'}")
