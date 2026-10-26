# Fábrica de videos verticales

Plantillas y motor para hacer Reels/TikTok 1080×1920 «como código» (cada cuadro = función del tiempo), probados con Mi Repostería en octubre de 2026. Los usa la skill «fabrica-videos».

## Formatos
| # | Formato | Archivo | Duración | Producción |
|---|---|---|---|---|
| 1 | Demo de app (+ versión con gancho de avatar) | `demo-app.html`, `gancho-overlay.html`, `hibrido.py` | 15 s / ~19 s | Código (+ 2 clips de Higgsfield) |
| 2 | Explicador de venta | `explicador.html` | 30 s | Código + fotos de la página |
| 3 | Lanzamiento de marca | `lanzamiento.html` | 20 s | Código + 1 foto |
| 4 | Receta con voz en off | `receta-voz.tpl.html` + `receta.py` | ~27 s | Código + clip, foto y voz de Higgsfield |

## Motor
- `lib.js`: helpers (spring, keys, words, money, sfx).
- `render.py video.html sheet 0.5 | frames t1 t2 | mp4 30`: hoja de contacto, cuadros sueltos o MP4 mudo (Playwright).
- `audio.py out/x.sfx.json out/x.wav`: música 120 BPM + efectos sintetizados (`NOMUSIC=1` = solo efectos).
- `voz.py salida.wav parte1.wav parte2.wav…`: une la voz en partes (Higgsfield corta a 25 s) y da el inicio de cada frase.
- `mezcla.py video-silent.mp4 fondo.wav salida.mp4 [--voz voz.wav]`: música bajo la voz y -14 LUFS.
- `qa.py video.mp4`: hoja con zona segura de Reels, saltos de imagen y volumen.

## Cómo mejora
`LECCIONES.md` es la bitácora: la skill la lee antes de cada video y le agrega lo que aprobaste, rechazaste o corregiste (y los resultados en redes cuando los compartas). Las lecciones que se repiten pasan a las reglas de la skill.

## Uso rápido
```
cp -r marcas/mi-reposteria/assets ./assets
python3 render.py explicador.html sheet 0.5     # revisar
python3 render.py explicador.html mp4 30
python3 audio.py out/explicador.sfx.json out/explicador.wav
python3 mezcla.py out/explicador-silent.mp4 out/explicador.wav out/Explicador.mp4
python3 qa.py out/Explicador.mp4
```
