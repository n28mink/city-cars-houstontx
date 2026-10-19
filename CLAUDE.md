# City Cars Houston TX — contexto para Claude Code

## Qué es el negocio
City Cars Houston TX NO es un dealer ni un prestamista. Es un puente entre compradores de Houston
(hispanos y angloparlantes) y muchos dealers con licencia en Texas. El sitio muestra un catálogo
amplio sin cotizaciones ni montos: solo la descripción de cada vehículo (año, millas, tipo, equipamiento).
Toda la conversión va a WhatsApp (+1 281 602 7044, horario 9 am–8 pm todos los días).
No hay backend ni base de datos.

## Estado actual (octubre 2026)
Este repo (`n28mink/city-cars-houston`) es la continuación de un proyecto que empezó en otro repo
(`N28INK/N28`, mismo negocio, mismo modelo de datos) y que avanzó mucho más acá: es el repo
**oficial de ahora en adelante**. El otro quedó en pausa por un problema de permisos de GitHub
que no se pudo resolver; no se sigue tocando.

- **526 vehículos** (octubre 2026). Fuente: `inventario-nuevo/inventario.csv` (id, carpeta, año, marca, modelo,
  tipo, color, millas, num_fotos) + fotos originales en `inventario-nuevo/<año-marca-modelo-color>/` (NO se publican:
  `.vercelignore`) + WebP 640/1200 en `inventario-nuevo-web/<carpeta>/<n>-640|1200.webp` (SÍ se publican; el sitio las usa).
  `python3 -I tools/build-inventory.py` regenera `js/vehicles.js` (compacto; construye `VEHICLES` con el mismo esquema
  de antes), las 1052 fichas `/es/carro/<slug>/` y `/en/car/<slug>/` y reescribe el CSV. Dato que falta = "por confirmar"
  (`milesText()` / `yearText()` en `vehicles.js`); nunca inventar. Tipo/3 filas/4x4 se deducen del modelo o del nombre
  de la carpeta. **Nunca montos:** el CSV original traía `down_payment` y "$… down payment" en `nombre_original`;
  el script solo los lee para extraer año/millas y no los escribe en ningún archivo.
- Inventario en la home: buscador (`#q-inv`, palabras en cualquier orden), filtros (Trocas/SUV/Sedanes/3 filas/4x4)
  y paginación de 24 en 24 ("Ver más"). Fichas con `<th scope="row">`, visor con miniaturas y `aria-live`.
- Accesibilidad (auditoría oct 2026): verde de WhatsApp `#0F7A40` (≥4.5:1), foco atrapado en el modal, `aria-label` en
  el chat, 404 sin estilo/script inline, objetivos táctiles de 44 px.
- **Asistente/chat** (`js/assistant.js`, `css/assistant.css`): widget flotante que guía al
  visitante y arma el mensaje de WhatsApp. El texto del usuario se pasa por `esc()` (escapa `<` y
  `>`) antes de `innerHTML`; es una mitigación razonable pero no es `textContent` puro — si se toca
  este archivo, preferir `textContent` donde se pueda sin romper el layout del chat.
- `js/app.js`: inventario → tarjetas, filtros, favoritos, planificador. `js/i18n.js`: todos los
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
