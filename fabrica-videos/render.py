"""Render an HTML video (window.seek(t)) to frames / contact sheet / mp4.
usage: python3 render.py video1.html sheet 0.5          -> sheet of frames every 0.5s
       python3 render.py video1.html frames 1.0 9.3 ...  -> individual frames
       python3 render.py video1.html mp4 30               -> silent mp4 at fps
"""
import sys, json, subprocess, pathlib, io
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

here = pathlib.Path(__file__).parent
src, mode = sys.argv[1], sys.argv[2]
name = pathlib.Path(src).stem
out = here / "out"; out.mkdir(exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.goto((here / src).resolve().as_uri())
    pg.evaluate("document.fonts.ready"); pg.evaluate("window.READY || null")
    pg.wait_for_timeout(300)
    dur = pg.evaluate("window.DUR")
    (out / f"{name}.sfx.json").write_text(json.dumps({"dur": dur, "drop": pg.evaluate("window.DROP"), "sfx": pg.evaluate("window.SFX"), "brk": pg.evaluate("window.BREAK || null")}))

    def shot(t, fmt="jpeg"):
        pg.evaluate(f"seek({t})")
        return pg.screenshot(type=fmt, quality=93) if fmt == "jpeg" else pg.screenshot(type="png")

    if mode == "sheet":
        step = float(sys.argv[3]); ts = []
        t = 0.0
        while t < dur - 1e-6: ts.append(round(t, 3)); t += step
        cols = 6; w, h = 270, 480
        rows = (len(ts) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * (h + 28)), "white")
        d = ImageDraw.Draw(sheet)
        for n, t in enumerate(ts):
            im = Image.open(io.BytesIO(shot(t))).resize((w, h))
            x, y = (n % cols) * w, (n // cols) * (h + 28)
            sheet.paste(im, (x, y + 28)); d.text((x + 6, y + 6), f"{t:.2f}s", fill="black")
        sheet.save(out / f"{name}-sheet.png"); print(out / f"{name}-sheet.png")
    elif mode == "frames":
        for t in sys.argv[3:]:
            f = out / f"{name}-{t}.png"; f.write_bytes(shot(float(t), "png")); print(f)
    elif mode == "mp4":
        fps = int(sys.argv[3]); n = int(round(dur * fps))
        mp4 = out / f"{name}-silent.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)], stdin=subprocess.PIPE)
        for i in range(n):
            ff.stdin.write(shot(i / fps))
            if i % 90 == 0: print(f"frame {i}/{n}", flush=True)
        ff.stdin.close(); ff.wait(); print(mp4)
    b.close()
