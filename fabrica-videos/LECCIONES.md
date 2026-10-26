# Bitácora de lecciones de la fábrica

La skill «fabrica-videos» lee este archivo ANTES de producir y le agrega una entrada DESPUÉS de cada entrega.
Así cada video aprovecha lo aprendido en los anteriores.

## Cómo se usa
1. **Antes de producir:** lee «Pendientes de consolidar» y las entradas del mismo formato y marca. Aplica lo que diga, aunque todavía no esté en las reglas de la skill.
2. **Después de entregar:** agrega una entrada en el Registro (la más nueva arriba) con lo que el usuario aprobó, rechazó o corrigió, y el porqué en sus palabras.
3. **Cuando el usuario comparta resultados** (vistas, retención a los 3 s, comentarios con la palabra clave, ventas), anótalos en la entrada de ese video. Es la señal más valiosa: dice qué vende, no solo qué se ve bien.
4. **Consolidar:** si una lección se repite 2 veces o el usuario la pide como regla, pásala a las «Reglas de calidad» de la skill, muévela a «Ya consolidadas» y sube el cambio al fork.

## Cómo leer los resultados de un video
Pide al usuario estas cifras de Instagram (Estadísticas del Reel) unos 3–7 días después de publicar:
| Cifra | Cálculo | Qué mide | Si sale baja, cambia… |
|---|---|---|---|
| Retención del gancho | reproducciones de 3 s ÷ impresiones (o «% que siguió viendo después de 3 s») | el gancho | solo los primeros 3 s (prueba otro gancho con `ganchos.py`) |
| Retención al final | % que vio hasta el CTA | la historia y el ritmo | el orden o la duración de las escenas; quita texto |
| Comentarios con la palabra | comentarios «COSTO» ÷ reproducciones | el cierre y la oferta | el CTA, el precio en pantalla o el gancho de la oferta |
| Ventas | ventas ÷ conversaciones de ManyChat | el mensaje de ManyChat y la página, no el video | nada del video |
Nunca atribuyas el resultado a un solo elemento con una sola publicación; compara con los otros videos del mismo formato y anota la hipótesis.

## Prueba de ganchos
Cada video sale con su gancho principal y 2 variantes (`ganchos.py`). Anota en la entrada qué gancho usó cada versión y cuál ganó (retención de 3 s). La hipótesis se escribe para que pueda perder, por ejemplo: «El gancho de pregunta con precio supera al de dolor en retención de 3 s, en reposteras que ya venden».

## Revisión mensual
Una vez al mes, agrega una entrada «Revisión <mes>» con: ganadores (cifras y qué elemento lo logró), perdedores (en qué cifra murieron y por qué creemos), métricas sueltas que salieron bien en un video perdedor, aprendizajes nuevos (pásalos a «Pendientes de consolidar») y el plan de pruebas del mes siguiente.

## Pendientes de consolidar
_(vacío: todo lo aprendido hasta ahora ya está en las reglas de la skill)_

## Registro

### 2026-10-26 · Mi Repostería · Historia emocional ilustrada (49 s)
- Resultado: entregado, después **descartado como formato** por el usuario.
- Lección: no ofrecer este formato. Consolidada («No usar historia emocional ilustrada»).

### 2026-10-26 · Mi Repostería · Receta con voz v3 (27 s)
- Resultado: entregada; es la versión que quedó como plantilla del formato 4.
- Qué cambió frente a la v2: voz en off (Marisol) que cuenta la historia, una idea por escena, escenas sincronizadas con las frases, foto y clip reales al inicio y al final.
- Problema técnico: la música tapaba la voz → sidechain con la música 11 dB abajo y -14 LUFS (`mezcla.py`).
- Resultados en redes: _pendiente_.

### 2026-10-26 · Mi Repostería · Receta v2 (20 s, sin voz)
- Resultado: **rechazada**. Palabras del usuario: «demasiado rápido y no logro entender el contenido rápidamente, tampoco me genera deseo de seguir viendo».
- Lecciones (consolidadas en las reglas 2, 3 y 6): ritmo de lectura mínimo, una idea por escena y voz en off en recetas o videos de más de 20 s.

### 2026-10-26 · Mi Repostería · Receta v1 (22 s)
- Resultado: **rechazada**: diagramas sin comida real.
- Lección (consolidada en la regla 7): comida real de Higgsfield al inicio y al final; los diagramas no dan antojo.

### 2026-10-26 · Mi Repostería · Lanzamiento v2 (20 s)
- Resultado: aprobado; es la plantilla del formato 3.
- Qué cambió frente a la v1: gancho con foto del problema, cifra clave gigante en el golpe, 3 pasos con tarjetas grandes y cierre con precio y CTA.

### 2026-10-26 · Mi Repostería · Lanzamiento v1 (27 s)
- Resultado: **rechazado**. Efectos tipo keynote sin mensaje (cuadrícula, bento, estados de pedido).
- Lección (consolidada en el módulo 3): cada efecto debe cargar un mensaje; nada de «presentamos» ni logos al inicio (regla 1).

### 2026-10-26 · Mi Repostería · Demo 15 s, explicador 30 s y demo híbrida con avatar
- Resultado: entregados y aprobados; son las plantillas de los formatos 1 y 2.
- Problemas técnicos resueltos (consolidados en la regla 11): `words()` con `Infinity` da NaN; letras con descendentes se cortaban en las máscaras; fantasmas con `visibility:hidden`; saltos de un cuadro en cambios de color.
- Higgsfield: la voz corta a 25 s (generar en partes); lotes con 429 (reintentar solo los que fallan); la descarga necesitó permitir los dominios en Settings.

## Ya consolidadas
Todas las lecciones del registro de arriba (2026-10-26) ya están en la skill.
