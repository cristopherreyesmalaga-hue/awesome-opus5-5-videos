"""Une las partes de la voz en off y deja pausas parejas; imprime cuándo empieza cada frase.

Higgsfield (seed_audio) corta el audio a los 25 s, así que el guion se genera en partes cortas.
uso: python3 voz.py salida.wav parte1.wav [parte2.wav ...] [--min 0.25] [--max 0.8] [--entre 0.9] [--inicio 0.3] [--corte 0.18]
  --min/--max  límite de las pausas dentro de una parte (s)
  --entre      pausa entre partes (s)
  --inicio     silencio al principio (s)
  --corte      pausa mínima que separa frases; súbelo si corta frases a la mitad, bájalo si junta varias
Salida (JSON): {"frases": [{"n": 0, "parte": 1, "inicio": 0.3, "fin": 2.1}, ...], "duracion": 24.8}
Usa "inicio" de cada frase para sincronizar las escenas.
"""
import sys, json, subprocess, argparse
import numpy as np
from scipy.io import wavfile

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument("salida"); ap.add_argument("partes", nargs="+")
ap.add_argument("--min", type=float, default=0.25); ap.add_argument("--max", type=float, default=0.8)
ap.add_argument("--entre", type=float, default=0.9); ap.add_argument("--inicio", type=float, default=0.3)
ap.add_argument("--umbral", type=float, default=-50, help="dB para considerar silencio")
ap.add_argument("--corte", type=float, default=0.18, help="pausa mínima (s) que separa dos frases")
a = ap.parse_args()

def cargar(f):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def frases(x, pad=0.04):
    min_sil = a.corte
    h = int(SR * 0.01)
    e = np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-9 for i in range(0, len(x) - h, h)])
    on = 20 * np.log10(e) > a.umbral
    segs, i, n, gap = [], 0, len(on), int(min_sil / 0.01)
    while i < n:
        if not on[i]: i += 1; continue
        j = i
        while True:
            while j < n and on[j]: j += 1
            k = j
            while k < n and not on[k]: k += 1
            if k >= n or k - j >= gap: break
            j = k
        segs.append([max(0.0, i * 0.01 - pad), min(len(x) / SR, j * 0.01 + pad)]); i = j
    return segs

out, t, lista, n = [np.zeros(int(SR * a.inicio), np.float32)], a.inicio, [], 0
for p, f in enumerate(a.partes, 1):
    x = cargar(f); sg = frases(x)
    for k, (s0, s1) in enumerate(sg):
        seg = x[int(s0 * SR):int(s1 * SR)].copy(); fd = int(0.01 * SR)
        seg[:fd] *= np.linspace(0, 1, fd); seg[-fd:] *= np.linspace(1, 0, fd)
        lista.append({"n": n, "parte": p, "inicio": round(t, 3), "fin": round(t + len(seg) / SR, 3)}); n += 1
        out.append(seg); t += len(seg) / SR
        if k < len(sg) - 1:
            g = min(a.max, max(a.min, sg[k + 1][0] - s1))
        else:
            g = a.entre if p < len(a.partes) else 0.0
        out.append(np.zeros(int(SR * g), np.float32)); t += g
y = np.concatenate(out); y /= max(1e-6, np.abs(y).max()) / 0.9
wavfile.write(a.salida, SR, (y * 32767).astype(np.int16))
print(json.dumps({"frases": lista, "duracion": round(len(y) / SR, 3)}, ensure_ascii=False))
