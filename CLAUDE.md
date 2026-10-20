# City Cars Houston TX — contexto para Claude Code

## Qué es el negocio
City Cars Houston TX NO es un dealer ni un prestamista. Es un puente entre compradores de Houston
(hispanos y angloparlantes) y muchos dealers con licencia en Texas. El sitio muestra un catálogo
amplio sin cotizaciones ni montos: solo la descripción de cada vehículo (año, millas, tipo, equipamiento).
Toda la conversión va a WhatsApp (+1 281 602 7044, horario 9 am–8 pm todos los días).
No hay backend ni base de datos.

## Estado actual (octubre 2026)
Este repo (`n28mink/city-cars-houstontx`) es la continuación de un proyecto que empezó en otro repo
(`N28INK/N28`, mismo negocio, mismo modelo de datos) y que avanzó mucho más acá: es el repo
**oficial de ahora en adelante**. El otro quedó en pausa por un problema de permisos de GitHub
que no se pudo resolver; no se sigue tocando.

### Rediseño (oct 2026)
Rediseño completo con **Carvana, Rivian y Porsche** como referentes (informe "Referentes diseño web automotriz"). Vive en la rama
`rediseno` y se ve primero en su vista previa de Vercel; **no se fusiona a `main` hasta que el dueño lo apruebe**. Todo el porqué, los
tokens, los componentes y las mediciones están en **`design.md`**. Resumen:
- Idea: **foto real primero**. Hero a sangre con la foto de CCH-526 (Ram 1500 Rebel azul; `HERO_ID` en `tools/build-inventory.py`, `img/hero.webp` y `img/hero-m.webp`), titular
  "Una conversación, muchos dealers.", una sola acción (WhatsApp). Si esa unidad se da de baja el generador se detiene para que se elija otra foto (y se vuelva a medir el contraste del texto).
- Orden de la home: Hero → Inventario → ¿Cuál es tu caso? → Lo que sí hacemos (4 afirmaciones reales, sin reseñas ni conteos) → Cómo funciona → Requisitos → Calculadora → Vende tu carro → Preguntas → Pie.
- Marca: logo "puente" (dos C que se entrelazan, verde `#0F5A3C` y azul `#0E5AA7`) hecho por Claude a pedido del dueño y reemplazable (`img/logo*.svg`, `favicon.svg`, `img/apple-touch-icon.png`).
  El azul es la marca; **el verde es solo de WhatsApp**; el amarillo es señal. Fuente **Instrument Sans** variable autoalojada (`fonts/instrument-sans-var.woff2`; sustituye a Overpass).
- Cabecera y pie compartidos: se editan solo en `tools/chrome.py` y se estampan con `python3 -I tools/stamp-chrome.py` (8 páginas estáticas); las fichas los toman del mismo módulo al regenerar.
- Imágenes para compartir en WhatsApp/Facebook: `img/og/<slug>.jpg` por ficha (`python3 -I tools/build-og.py`, Pillow) y `img/og-es.jpg`/`img/og-en.jpg` de la portada (`tools/og-home.html`).
- Decisiones del dueño que se respetaron frente al informe: una sola foto frontal por tarjeta (todas en la ficha), fotos completas (nunca recortadas), "usado" siempre visible (se suma la etiqueta "Pocas millas" por debajo de 5,000 millas), sin montos ni prueba social inventada.
- El aviso de marcas del pie se reescribió (antes nombraba Chevrolet, GMC, Jeep y Kia) y lleva la marca visible `[REVISAR CON ABOGADO]` hasta que el dueño lo confirme (`tools/chrome.py`).
- Se hizo con las skills `frontend-design` y `ui-ux-pro-max`, instaladas a mano en el contenedor de Claude: no están en el repo y se pierden al reiniciar.

### Inventario y datos
- **Fotos con fondo blanco DADAS DE BAJA del sitio (decisión del dueño, oct 2026).** Se publicaron un día (570 vehículos) y se
  retiraron: el sitio vuelve a usar solo las fotos normales (foto 1 = portada frontal elegida a ojo, columna `portada`).
  Las 93 unidades que solo tenían fotos blancas quedaron con `publicar=no` (sin foto no se publican). `fotos-blancas/` y
  `tools/import-fotos-blancas.py` siguen en el repo por si se retoman (la carpeta NO se publica: `.vercelignore`; sus nombres traen
  montos). **476 vehículos publicados** (CCH-501 dado de baja: sus fotos eran de una Silverado ZR2, no de un Tucson). Las fichas conservan "Especificaciones del modelo" desde
  `inventario-nuevo/especificaciones.json` (JSON del dueño SIN `down_payment_usd`; típicas del año/modelo, el dealer confirma la
  unidad; en inglés se traducen con reglas `EN_RULES`). El modelo/versión salen de la columna `nombre` (nombre limpio, sin montos).
- **Etiquetas de color corregidas (oct 2026):** en CCH-505, 509, 517, 522, 524 y 525 el color del CSV no coincidía con NINGUNA de sus fotos (todas las fotos exteriores coincidían entre sí y con el modelo),
  así que se ajustó el CSV al color que se ve (505 negro, 509 blanco, 517 negro, 522 blanco, 524 negro, 525 blanco). El `slug` sale de la carpeta, por eso esas URLs conservan la palabra de color vieja
  (p. ej. `…-suburban-rst-…-azul` es una Suburban negra). Regla: si foto y ficha se contradicen, se corrige la etiqueta o se da de baja la unidad; nunca se deja la contradicción.
- **Reglas del CSV y del generador.** Decisión del dueño: solo se publican vehículos
  **2017 o más nuevos** (`MIN_YEAR` en el generador); los 24 anteriores (o sin año) y 25 duplicados (la misma unidad en dos carpetas, detectada por fotos casi idénticas y revisada
  a ojo) quedan con `publicar=no` en el CSV,
  sin fichas ni WebP publicados (sus originales siguen en `inventario-nuevo/`). Fuente: `inventario-nuevo/inventario.csv`
  (id, carpeta, anio, marca, modelo, tipo, color, millas, num_fotos, **portada**, **publicar**, **nombre**; `nombre` = nombre limpio del dealer SIN montos, de donde sale el modelo/versión/4x4) + fotos originales en
  `inventario-nuevo/<año-marca-modelo-color>/` (NO se publican: `.vercelignore`) + WebP 640/1200 en
  `inventario-nuevo-web/<carpeta>/<n>-640|1200.webp` (SÍ se publican; el sitio las usa).
  `python3 -I tools/build-inventory.py` regenera `js/vehicles.js` (compacto; construye `VEHICLES`), una ficha por vehículo publicado,
  `/es/carro/<slug>/` y `/en/car/<slug>/`, el pie de foto del hero y reescribe el CSV. Dato que falta = "por confirmar"
  (`milesText()` / `yearText()` en `vehicles.js`); nunca inventar. Tipo/3 filas/4x4 se deducen del modelo o del nombre
  de la carpeta. **Nunca montos:** el CSV original traía `down_payment` y "$… down payment" en `nombre_original`;
  el script solo los lee para extraer año/millas y no los escribe en ningún archivo.
- **Orden "los mejores primero"**: año más nuevo y, a igual año, menos millas (sin millas al final). Lo calcula el
  generador (orden de `vehicles.js`, campo `rank`); el visitante puede cambiarlo con "Ordenar por".
- **Portada frontal**: la tarjeta muestra UNA sola foto, la frontal (foto 1; `portada` en el CSV por si hay que
  cambiarla). Todas las fotos se ven solo en la ficha del vehículo. No hay modal ni deslizador en las tarjetas.
- **Fotos completas, sin recorte**: tarjetas y ficha usan `object-fit: contain` sobre un fondo que es la misma foto desenfocada (se asigna por CSSOM al cargar, porque la CSP
  no permite `style=""`). En la ficha, tocar la foto (o el botón de ampliar) abre un visor de UNA foto (`js/viewer.js`): pellizcar para acercar, arrastrar, doble toque, rueda,
  flechas/deslizar para cambiar de foto, Esc cierra. Fichas con `<th scope="row">`, miniaturas y `aria-live`.
- **Fotos limpias (oct 2026)**: el dueño reemplazó en `inventario-nuevo/<carpeta>/N.jpg` las fotos con el MISMO nombre por versiones
  sin letreros/placas. Para regenerar los WebP tras cualquier cambio de fotos: `python3 -I tools/rebuild-webp.py` y luego
  `python3 -I tools/build-inventory.py` (y `tools/build-og.py` si cambió alguna portada).

### Sitio (JS, filtros, accesibilidad, seguridad, despliegue)
- Filtros del inventario: barra superior de menús desplegables de solo texto (Marca con conteos, Modelo dependiente, Año desde/hasta, Color, Millas) + buscador + "Ordenar por" + chips de tipo
  (Todos/Trocas/SUV/Sedanes/3 filas/4x4 confirmada). Sin muestras ni iconos de color. Celular: los filtros abren como hoja desde abajo (botón "Filtros (n)", "Ver N vehículos", foco atrapado, Esc cierra).
  Los filtros activos salen como etiquetas que se quitan con un toque + "Limpiar filtros". El estado vive en la URL (`?marca=&modelo=&desde=&hasta=&color=&millas=&orden=&tipo=&q=`, lista
  blanca) para que "Volver al inventario" desde una ficha conserve los filtros. Paginación de 24 en 24.
- `js/app.js`: `initHome()` (casos, inventario, tarjetas, filtros, favoritos, redirección de enlaces viejos, observador del hero) y `initPlan()` (formulario «Crea tu plan»);
  cada una corre solo si existe su elemento (`#grid` / `#planform`). El plan es página propia: `es/plan/`, `en/plan/`
  (acepta `?vehiculo=` y `?caso=`, ambos con lista blanca; `planHref()` arma los enlaces). «Lo que NO hacemos»: `es/que-no-hacemos/`, `en/what-we-dont-do/`.
  Ninguna de las dos va en la portada; el menú enlaza al plan y el pie a «NO hacemos». `js/i18n.js`: todos los
  textos ES/EN. `js/specs.js`: specs mecánicas investigadas por modelo. Orden de carga fijo con `defer`: `vehicles.js` → `specs.js` → `i18n.js` → `app.js` (+ `viewer.js` en las fichas).
- Sin asistente/chat flotante: se eliminó por decisión del dueño (no recrearlo sin pedirlo).
- Accesibilidad (auditorías oct 2026): verde de WhatsApp `#0F7A40` (≥4.5:1), 404 sin estilo/script inline, objetivos táctiles de 44 px, anillo de foco azul sobre claro y amarillo sobre oscuro
  (el amarillo sobre fondo claro daba 1.65:1), hover oscuro del botón azul ≥4.5:1, texto del hero sobre la foto medido (≥3:1 el titular, ≥4.5:1 el resto, en 320–1366 px).
- **Seguridad:**
  - La CSP real va por cabecera en `vercel.json` (`default-src 'self'`; `style-src 'self'`; `script-src 'self'`; `frame-ancestors 'none'`…). Solo las dos portadas llevan además una CSP en `<meta>`.
    `img-src` todavía permite `drive.google.com` y `*.googleusercontent.com` aunque ya no queda ninguna foto allí: se puede cerrar.
  - `vercel.json` también pone HSTS, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` y `Cross-Origin-Opener-Policy`. Sin paso de build: Vercel con Root Directory vacío (el sitio
    vive en la raíz del repo) y Framework "Other".
  - `.well-known/security.txt` con el WhatsApp oficial como contacto.
  - Ninguna página lleva estilos ni scripts inline (las 952 fichas `/es/carro/…` y `/en/car/…` tampoco); el visor lee `<script type="application/json" id="photos-data">`.
- **Despliegue:** Vercel proyecto `city-cars-houstontx` (equipo `n28mink-6615`, cuenta n28mink@gmail.com), conectado a este repo; cada push a `main` publica solo (rama principal de GitHub: `main`).
  Cada push a otra rama genera una vista previa propia en Vercel (así se revisa el rediseño antes de publicarlo).
- **URL pública:** `https://city-cars-houstontx.vercel.app/` ya está puesta en JSON-LD, `sitemap.xml`, canonical/hreflang y etiquetas `og:` de las páginas. Si se conecta un dominio propio,
  reemplazarla en todo el repo (y volver a correr los generadores).

### Abiertos
- Confirmar año/millas/condición de cada vehículo con el dealer; llenar los `[COMPLETAR]` de la política de privacidad; confirmar el aviso de marcas del pie (quitar su `[REVISAR CON ABOGADO]`).
- Auditar las etiquetas de color y modelo de las 476 unidades contra sus fotos (en la última pasada, 6 de las 24 más nuevas estaban mal).
- Conectar el dominio propio del dueño al proyecto de Vercel (pendiente).
- `index.html` de la raíz tiene un `<script>` inline para elegir idioma que la CSP bloquea: hoy `<meta refresh>` manda a todos a `/es/`, incluso a quien navega en inglés.
- `sitemap.xml` solo lista las 8 páginas estáticas; las fichas no están (se descubren por JS desde la portada).
- Vercel Web Analytics no está activado en el proyecto (se quitó de las páginas de privacidad un `<script>` de `/_vercel/insights` que daba 404). Medir clics a WhatsApp requeriría activarlo y añadirlo a todas las páginas.

## Diseño
Lee **`design.md`** antes de tocar HTML/CSS/JS: marca y logo, tokens de color y tipografía, componentes (cabecera, hero, botones, chips, tarjetas,
filtros, ficha, plan), reglas de fotos, movimiento, accesibilidad, cómo se construye y lista de revisión. Si cambias un token o un componente,
actualiza `design.md` en el mismo commit.

## Reglas (igual que siempre)
- Nunca precios, inicial, mensualidad, APR ni plazos en ningún texto ni mensaje de WhatsApp.
- Frases prohibidas (43 TAC §215.247): "financiamos a todos", "aprobación garantizada", "sin
  importar tu crédito", "everyone approved". Usar: "Muchos de nuestros dealers trabajan con ITIN,
  sin crédito o crédito dañado."
- No agregar dependencias ni frameworks sin preguntar.
- No inventar datos de vehículos, reseñas ni número de dealers asociados.
- No usar logos de marcas como elementos de marca.
- Cualquier texto legal nuevo lleva marca `[REVISAR CON ABOGADO]` hasta que el dueño lo confirme.
- Enlaces WhatsApp con `new URL()` + `searchParams`, `rel="noopener noreferrer"`.
