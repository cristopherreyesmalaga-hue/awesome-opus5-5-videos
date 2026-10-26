"""Combine two Higgsfield clips (hook) + the coded app demo into one vertical ad.
usage: python3 assemble.py clipA.mp4 clipB.mp4 out/<Marca>-Demo-con-avatar.mp4
Structure: clip A (3s, hook text) -> clip B (3s, "Ahora sí lo sé") -> demo-app from 2.15s (phone rises) to end.
"""
import sys, json, subprocess, pathlib, io
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
clipA, clipB, final = sys.argv[1], sys.argv[2], sys.argv[3]
out = here / "out"; tmp = here / "tmp"; tmp.mkdir(exist_ok=True)
FPS, A, CUT = 30, 3.0, 2.15  # CUT: where video1 continues (hook text already shown over the clips)

def run(cmd): subprocess.run(cmd, check=True)

# 1) Overlay frames with alpha (hook text over the real clips)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto((here / "gancho-overlay.html").resolve().as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
                          "-c:v", "qtrle", str(tmp / "overlay.mov")], stdin=subprocess.PIPE)
    for i in range(int(2 * A * FPS)):
        pg.evaluate(f"seek({i / FPS})"); ff.stdin.write(pg.screenshot(type="png", omit_background=True))
    ff.stdin.close(); ff.wait(); b.close()

# 2) Hook = clip A + clip B scaled/cropped to 1080x1920, trimmed to 3s each, no original audio
vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},setsar=1"
for n, c in (("a", clipA), ("b", clipB)):
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", c, "-t", str(A), "-vf", vf + f",tpad=stop_mode=clone:stop_duration={A}", "-t", str(A), "-an",
         "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(tmp / f"hook_{n}.mp4")])
run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "hook_a.mp4"), "-i", str(tmp / "hook_b.mp4"),
     "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(tmp / "hook.mp4")])
run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "hook.mp4"), "-i", str(tmp / "overlay.mov"),
     "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[v]", "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(tmp / "hook_txt.mp4")])

# 3) App demo continues from CUT
run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(CUT), "-i", str(out / "demo-app-silent.mp4"), "-an",
     "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(tmp / "demo_tail.mp4")])
run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "hook_txt.mp4"), "-i", str(tmp / "demo_tail.mp4"),
     "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", str(tmp / "full_silent.mp4")])

# 4) Audio: same music engine, sound events shifted to the new timeline
v1 = json.loads((out / "demo-app.sfx.json").read_text())
shift = 2 * A - CUT
ev = [[t + shift, k] for t, k in v1["sfx"] if t >= CUT - 0.05 and k != "thud"]
ev += [[0.1, "thud"], [0.55, "thud"], [1.0, "thud"], [A - 0.1, "whoosh"], [A + 0.15, "pop"], [A + 0.9, "sparkle"], [2 * A - 0.1, "whoosh"]]
dur = round(2 * A + (v1["dur"] - CUT), 3)
(tmp / "combo.sfx.json").write_text(json.dumps({"dur": dur, "drop": v1["drop"] + shift, "sfx": ev}))
run(["python3", str(here / "audio.py"), str(tmp / "combo.sfx.json"), str(tmp / "combo.wav")])
run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "full_silent.mp4"), "-i", str(tmp / "combo.wav"),
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final])
print(final, dur, "s")
