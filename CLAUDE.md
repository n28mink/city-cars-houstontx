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

- **Fotos con fondo blanco DADAS DE BAJA del sitio (decisión del dueño, oct 2026).** Se publicaron un día (570 vehículos) y se
  retiraron: el sitio vuelve a usar solo las fotos normales (foto 1 = portada frontal elegida a ojo, columna `portada`).
  Las 93 unidades que solo tenían fotos blancas quedaron con `publicar=no` (sin foto no se publican). `fotos-blancas/` y
  `tools/import-fotos-blancas.py` siguen en el repo por si se retoman (la carpeta NO se publica: `.vercelignore`; sus nombres traen
  montos). **477 vehículos publicados.** Las fichas conservan "Especificaciones del modelo" desde
  `inventario-nuevo/especificaciones.json` (JSON del dueño SIN `down_payment_usd`; típicas del año/modelo, el dealer confirma la
  unidad; en inglés se traducen con reglas `EN_RULES`). El modelo/versión salen de la columna `nombre` (nombre limpio, sin montos).
  
- **Reglas del CSV y del generador.** Decisión del dueño: solo se publican vehículos
  **2017 o más nuevos** (`MIN_YEAR` en el generador); los 24 anteriores (o sin año) y 25 duplicados (la misma unidad en dos carpetas, detectada por fotos casi idénticas y revisada
  a ojo) quedan con `publicar=no` en el CSV,
  sin fichas ni WebP publicados (sus originales siguen en `inventario-nuevo/`). Fuente: `inventario-nuevo/inventario.csv`
  (id, carpeta, anio, marca, modelo, tipo, color, millas, num_fotos, **portada**, **publicar**, **nombre**; `nombre` = nombre limpio del dealer SIN montos, de donde sale el modelo/versión/4x4) + fotos originales en
  `inventario-nuevo/<año-marca-modelo-color>/` (NO se publican: `.vercelignore`) + WebP 640/1200 en
  `inventario-nuevo-web/<carpeta>/<n>-640|1200.webp` (SÍ se publican; el sitio las usa).
  `python3 -I tools/build-inventory.py` regenera `js/vehicles.js` (compacto; construye `VEHICLES`), una ficha por vehículo publicado,
  `/es/carro/<slug>/` y `/en/car/<slug>/` y reescribe el CSV. Dato que falta = "por confirmar"
  (`milesText()` / `yearText()` en `vehicles.js`); nunca inventar. Tipo/3 filas/4x4 se deducen del modelo o del nombre
  de la carpeta. **Nunca montos:** el CSV original traía `down_payment` y "$… down payment" en `nombre_original`;
  el script solo los lee para extraer año/millas y no los escribe en ningún archivo.
- Hero en celular (≤900 px): el bloque "¿Por dónde quieres empezar?" (`.start`) va ARRIBA del letrero verde (CSS `order:-1`,
  el HTML sigue con el h1 primero). En escritorio queda en la columna derecha como antes.
- **Orden "los mejores primero"**: año más nuevo y, a igual año, menos millas (sin millas al final). Lo calcula el
  generador (orden de `vehicles.js`, campo `rank`); el visitante puede cambiarlo con "Ordenar por".
- **Portada frontal**: la tarjeta muestra UNA sola foto, la frontal con fondo blanco (foto 1; `portada` en el CSV por si hay que
  cambiarla). Todas las fotos se ven solo en la ficha del vehículo. No hay modal ni deslizador en las tarjetas.
- Home: el INVENTARIO va primero, antes de todo el texto. Escritorio: columna de filtros fija a la izquierda (Marca con conteos,
  Modelo dependiente, Año desde/hasta, Color con muestras, Millas) + buscador grande, orden y botones de tipo
  (Todos/Trocas/SUV/Sedanes/3 filas/4x4) arriba de las tarjetas. Celular: los filtros abren como hoja desde abajo (botón
  "Filtros (n)", botón "Ver N vehículos", foco atrapado, Esc cierra). Los filtros activos salen como etiquetas que se quitan con
  un toque + "Limpiar filtros". El estado vive en la URL (`?marca=&modelo=&desde=&hasta=&color=&millas=&orden=&tipo=&q=`, lista
  blanca) para que "Volver al inventario" desde una ficha conserve los filtros. Paginación de 24 en 24.
- **Fotos completas, sin recorte**: tarjetas y ficha usan `object-fit: contain` sobre fondo claro (`--photo-bg`). En la ficha, tocar la
  foto (o el botón de ampliar) abre un visor de UNA foto (`js/viewer.js`): pellizcar para acercar, arrastrar, doble toque, rueda,
  flechas/deslizar para cambiar de foto, Esc cierra. Fichas con `<th scope="row">`, miniaturas y `aria-live`.
- **Fotos limpias (oct 2026)**: el dueño reemplazó en `inventario-nuevo/<carpeta>/N.jpg` las fotos con el MISMO nombre por versiones
  sin letreros/placas. Para regenerar los WebP tras cualquier cambio de fotos: `python3 -I tools/rebuild-webp.py` y luego
  `python3 -I tools/build-inventory.py`.
- Accesibilidad (auditoría oct 2026): verde de WhatsApp `#0F7A40` (≥4.5:1), 404 sin estilo/script inline, objetivos táctiles de 44 px.
- Sin asistente/chat flotante: se eliminó por decisión del dueño (no recrearlo sin pedirlo).
- `js/app.js`: `initHome()` (casos, inventario, tarjetas, filtros, favoritos) y `initPlan()` (formulario «Crea tu plan»);
  cada una corre solo si existe su elemento (`#grid` / `#planform`). El plan es página propia: `es/plan/`, `en/plan/`
  (acepta `?vehiculo=` y `?caso=`, ambos con lista blanca). «Lo que NO hacemos»: `es/que-no-hacemos/`, `en/what-we-dont-do/`.
  Ninguna de las dos va en la portada; el menú enlaza al plan y el pie a «NO hacemos». `js/i18n.js`: todos los
  textos ES/EN. `js/specs.js`: specs mecánicas investigadas por modelo.
- **Seguridad:**
  - CSP ya puesta por `<meta http-equiv="Content-Security-Policy">` en cada página (no cubre
    `frame-ancestors`).
  - `vercel.json` (agregado ahora) pone lo que un `<meta>` no puede: HSTS, `X-Frame-Options`,
    `Referrer-Policy`, `Permissions-Policy`, `Cross-Origin-Opener-Policy`, y `frame-ancestors` en
    el CSP por header. Sin paso de build: Vercel debe quedar con Root Directory vacío (el sitio
    vive en la raíz del repo) y Framework "Other".
  - `.well-known/security.txt` con el WhatsApp oficial como contacto.
- **Páginas de carro y CSP (octubre 2026):** las 176 páginas `/es/carro/…` y `/en/car/…` ya no llevan
  `<style>` ni `<script>` inline (la CSP `style-src/script-src 'self'` los bloqueaba): el estilo está en
  `css/carro.css` y el visor de fotos en `js/viewer.js` (lee `<script type="application/json" id="photos-data">`).
  La CSP permite imágenes de `drive.google.com` y `*.googleusercontent.com` porque 72 fotos del inventario
  viven en Google Drive; la meta es migrarlas a `img/` en WebP (ver `photoSrc()` en `js/app.js`).
- **UI v3:** cabecera de vidrio, botones con brillo, tarjetas con resplandor al cursor, franja de datos
  (`.stats`, el número sale de `VEHICLES.length`), aparición al hacer scroll (`.rv`, respeta
  `prefers-reduced-motion`) y ficha con foto principal + miniaturas. Todo en JS/CSS plano, sin dependencias.
- **Despliegue:** Vercel proyecto `city-cars-houstontx` (equipo `n28mink-6615`, cuenta n28mink@gmail.com), conectado a este repo; cada push a `main` publica solo (rama principal de GitHub: `main`).
- **URL pública:** `https://city-cars-houstontx.vercel.app/` ya está puesta en JSON-LD, `sitemap.xml` y demás
  páginas (antes apuntaba a github.io). Si se conecta un dominio propio, reemplazarla en todo el repo.
- **Despliegue:** falta confirmar/crear el proyecto de Vercel para este repo y conectar el dominio
  propio (mismo proceso que se hizo para el repo anterior: conectar a GitHub, Root Directory vacío,
  sin build command).

## Diseño
Lee **`design.md`** antes de tocar HTML/CSS/JS: tokens de color y tipografía, componentes (cabecera, hero, botones, chips, tarjetas,
filtros, ficha, visor de fotos), reglas de fotos, movimiento, accesibilidad y lista de revisión. Si cambias un token o un componente,
actualiza `design.md` en el mismo commit.

## Reglas (igual que siempre)
- Nunca precios, inicial, mensualidad, APR ni plazos en ningún texto ni mensaje de WhatsApp.
- Frases prohibidas (43 TAC §215.247): "financiamos a todos", "aprobación garantizada", "sin
  importar tu crédito", "everyone approved". Usar: "Muchos de nuestros dealers trabajan con ITIN,
  sin crédito o crédito dañado."
- No agregar dependencias ni frameworks sin preguntar.
- No inventar datos de vehículos, reseñas ni número de dealers asociados.
- No usar logos de marcas como elementos de marca.
- Cualquier texto legal lleva marca `[REVISAR CON ABOGADO]` hasta que el dueño lo confirme.
- Enlaces WhatsApp con `new URL()` + `searchParams`, `rel="noopener noreferrer"`.
