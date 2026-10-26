"""Synthesize a warm 120 BPM music bed + UI sound effects, all in code (no downloads).
usage: python3 audio.py out/video1.sfx.json out/video1.wav
"""
import sys, json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
cfg = json.load(open(sys.argv[1]))
dur, drop, events = cfg["dur"], cfg["drop"], cfg["sfx"]
brk = cfg.get("brk")  # optional [start, end] quiet breakdown: pads only
N = int(SR * (dur + 0.6))
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)
BEAT = 0.5

def t_(n): return np.arange(n) / SR
def env(n, a=0.005, d=0.3):
    t = t_(n); return np.minimum(1, t / a) * np.exp(-t / d)
def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    sig = sig[: N - i]
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[i:i + len(sig), 0] += sig * gain * l * 1.41
    mix[i:i + len(sig), 1] += sig * gain * r * 1.41
def lp(x, f): return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def note(f): return 440 * 2 ** ((f - 69) / 12)

# ---------- instruments ----------
def kick():
    n = int(0.35 * SR); t = t_(n)
    f = 45 + 90 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.12)
def clap():
    n = int(0.22 * SR); x = hp(rng.standard_normal(n), 900) * env(n, 0.002, 0.06)
    return lp(x, 6000) * 0.6
def hat():
    n = int(0.06 * SR); return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 0.018) * 0.35
def ep(midi, length, vel=1.0):  # soft electric-piano-ish tone
    n = int(length * SR); t = t_(n); f = note(midi)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.25) + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.1)
    return x * env(n, 0.01, length * 0.6) * vel
def pluck(midi, vel=1.0):
    n = int(0.45 * SR); t = t_(n); f = note(midi)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.4 + np.sin(2 * np.pi * f * t)
    return lp(x * env(n, 0.003, 0.13), 3500) * vel
def bass(midi, length):
    n = int(length * SR); t = t_(n); f = note(midi)
    return lp(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t), 400) * env(n, 0.008, length * 0.7)

# progression: Fmaj7 - Am7 - Dm7 - Bbmaj7 (warm, sweet), one chord per bar (4 beats)
prog = [(53, [65, 69, 72, 76]), (57, [64, 67, 69, 72]), (50, [62, 65, 69, 72]), (46, [62, 65, 69, 70])]
import os
NOMUSIC = bool(os.environ.get("NOMUSIC"))
nbeats = 0 if NOMUSIC else int(dur / BEAT) + 1
for b in range(nbeats):
    t = b * BEAT; root, ch = prog[(b // 4) % 4]
    after = t >= drop - 1e-6
    quiet = bool(brk) and brk[0] - 1e-6 <= t < brk[1] - 1e-6
    if quiet:
        if b % 4 == 0:
            for m in ch: add(ep(m, 2.1, 0.12), t, pan=(m % 5 - 2) * 0.12)
        add(pluck(ch[b % 4] + 12, 0.07), t, pan=0.3 if b % 2 else -0.3)
        continue
    if b % 4 == 0:
        for m in ch: add(ep(m, 2.1, 0.13 if after else 0.1), t, pan=(m % 5 - 2) * 0.12)
        add(bass(root - 12 + 12, 1.9), t, 0.5 if after else 0.25)
    # arpeggio pluck on 8ths
    for h in range(2):
        m = ch[(b * 2 + h) % 4] + 12
        add(pluck(m, 0.13 if after else 0.09), t + h * BEAT / 2, pan=0.35 if h else -0.35)
    if after or b >= 4:
        add(kick(), t, 0.75 if after else 0.45)
        if b % 2 == 1: add(clap(), t, 0.45 if after else 0.3)
        for h in range(2): add(hat(), t + h * BEAT / 2, 0.8 if after else 0.5, pan=0.2)

# riser before the drop
n = int(1.0 * SR); r = hp(rng.standard_normal(n), 1500) * np.linspace(0, 1, n) ** 2 * 0.25
if not NOMUSIC: add(r, drop - 1.0)
if brk and not NOMUSIC: add(r, brk[1] - 1.0)

# ---------- sound effects ----------
def s_tap():
    n = int(0.05 * SR); return hp(rng.standard_normal(n), 2500) * env(n, 0.0005, 0.008) * 0.8 + np.sin(2 * np.pi * 1800 * t_(n)) * env(n, 0.0005, 0.01) * 0.4
def s_pop():
    n = int(0.12 * SR); t = t_(n); f = 900 * np.exp(-t / 0.03) + 500
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.04) * 0.6
def s_key():
    n = int(0.03 * SR); return hp(rng.standard_normal(n), 3000) * env(n, 0.0003, 0.006) * 0.55
def s_tick():
    n = int(0.08 * SR); return np.sin(2 * np.pi * 2400 * t_(n)) * env(n, 0.0005, 0.02) * 0.25
def s_whoosh():
    n = int(0.5 * SR); x = rng.standard_normal(n); k = np.linspace(0, 1, n)
    y = np.zeros(n)
    for i in range(10):  # sweeping band
        a, b = int(i * n / 10), int((i + 1) * n / 10)
        y[a:b] = lp(hp(x[a:b], 300 + 3000 * i / 10), 800 + 5000 * i / 10)
    return y * np.sin(np.pi * k) ** 2 * 0.5
def s_drop():
    n = int(0.9 * SR); t = t_(n); f = 38 + 60 * np.exp(-t / 0.08)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.35) * 0.9
def s_chime():
    n = int(1.2 * SR); t = t_(n)
    return sum(np.sin(2 * np.pi * note(m) * t) * np.exp(-t / 0.5) * g for m, g in [(84, 0.25), (88, 0.18), (91, 0.12)]) * env(n, 0.002, 2)
def s_sparkle():
    out = np.zeros(int(0.9 * SR))
    for i, m in enumerate([88, 91, 95, 100]):
        s = np.sin(2 * np.pi * note(m) * t_(int(0.5 * SR))) * env(int(0.5 * SR), 0.002, 0.15) * 0.12
        a = int(i * 0.07 * SR); out[a:a + len(s)] += s
    return out
def s_thud():
    n = int(0.25 * SR); t = t_(n); f = 70 + 120 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.08) * 0.55
FX = {"tap": s_tap, "pop": s_pop, "key": s_key, "tick": s_tick, "whoosh": s_whoosh, "drop": s_drop, "chime": s_chime, "sparkle": s_sparkle, "thud": s_thud}
for at, kind in events:
    add(FX[kind](), at, 0.9)

# master: fade out, soft limit, normalize to around -14 LUFS-ish (RMS proxy)
fade = int(0.8 * SR); end = int(dur * SR)
mix[end - fade:end] *= np.linspace(1, 0, fade)[:, None]; mix[end:] = 0
mix = np.tanh(mix * 1.2)
rms = np.sqrt(np.mean(mix[: end] ** 2)); mix *= 0.16 / max(rms, 1e-6)
mix = np.clip(mix, -0.97, 0.97)[:end]
wavfile.write(sys.argv[2], SR, (mix * 32767).astype(np.int16))
print(sys.argv[2], f"{dur}s")
