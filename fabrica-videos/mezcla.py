"""Mezcla final: música/efectos + voz en off (opcional) y une con el video. Deja el audio en -14 LUFS.

uso: python3 mezcla.py video-silent.mp4 fondo.wav salida.mp4 [--voz voz.wav] [--retraso 0] [--bajo 11]
  --voz      voz en off (de voz.py); si falta, solo se normaliza el fondo
  --retraso  segundos que se retrasa la voz respecto al video
  --bajo     cuántos dB queda la música por debajo de la voz (11 recomendado)
La música baja sola cuando habla la voz (sidechain).
"""
import argparse, subprocess, re, tempfile, os

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("fondo"); ap.add_argument("salida")
ap.add_argument("--voz"); ap.add_argument("--retraso", type=float, default=0.0); ap.add_argument("--bajo", type=float, default=11.0)
a = ap.parse_args()
tmp = tempfile.mkdtemp()

def lufs(f):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", f, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
def run(cmd): subprocess.run(cmd, check=True)

mix = os.path.join(tmp, "mix.wav")
if a.voz:
    d = int(a.retraso * 1000)
    vz = os.path.join(tmp, "voz.wav")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.voz, "-af", f"aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={d}|{d}", vz])
    g = (lufs(vz) - a.bajo) - lufs(a.fondo)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.fondo, "-i", vz, "-filter_complex",
         f"[1:a]asplit=2[v][v2];[v]apad[vp];[0:a]aresample=48000,volume={g:.2f}dB[b];"
         "[b][vp]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=400[bd];"
         "[bd][v2]amix=inputs=2:normalize=0:duration=first[m]", "-map", "[m]", mix])
else:
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.fondo, "-ar", "48000", mix])
gain = -14 - lufs(mix)
fin = os.path.join(tmp, "fin.wav")
run(["ffmpeg", "-y", "-loglevel", "error", "-i", mix, "-af", f"volume={gain:.2f}dB,alimiter=limit=0.89", "-ar", "48000", fin])
run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.video, "-i", fin, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-shortest", "-movflags", "+faststart", a.salida])
print(a.salida, "audio", round(lufs(a.salida), 1), "LUFS")
