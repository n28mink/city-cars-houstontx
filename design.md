# design.md — City Cars Houston TX

Sistema de diseño del sitio (rediseño de octubre 2026). **Léelo antes de tocar HTML/CSS/JS** y úsalo como referencia para cualquier página
o componente nuevo. La fuente de verdad en código es `css/styles.css` (tokens en `:root`) y `css/carro.css` (ficha del vehículo); este
documento explica el porqué y las reglas. Si cambias un token o un componente, actualiza este archivo en el mismo commit.

## 1. Qué es esta marca y por qué se ve así

City Cars Houston TX es un **puente** entre compradores de Houston (hispanos y angloparlantes) y dealers con licencia en Texas.
**No es dealer ni prestamista.** El diseño debe sentirse **confiable, directo y local**, nunca una plantilla genérica ni una vitrina de lujo.

Idea visual: **foto real primero.** Una foto verdadera de una troca del inventario a sangre completa, un titular enorme y condensado,
mucho aire y una sola acción (WhatsApp). Del antiguo "letrero de autopista" sobreviven los detalles: la línea amarilla de carretera
(`.dash`, `.exits`), el amarillo como señal y el asfalto (`--ink`) en las franjas oscuras.

### Referentes y qué se tomó de cada uno
El rediseño partió del informe "Referentes diseño web automotriz" y del pedido del dueño: **Carvana, Rivian y Porsche**.

| Referente | Se tomó | Se descartó o adaptó, y por qué |
|---|---|---|
| Carvana | Una acción por zona; la foto manda; tarjeta = foto + pocos datos + un botón; filtros arriba | Precios, cuotas y "preaprobación" (regla *sin montos*; aquí no hay solicitud de crédito); galería deslizable en la tarjeta (decisión del dueño: **una sola foto frontal**, todas en la ficha) |
| Rivian | Foto a sangre en el hero, titular grande, aire, una sola acción primaria | Reseñas, conteos de clientes o de dealers (no se inventan datos; solo hay afirmaciones reales en "Lo que sí hacemos") |
| Porsche | Tipografía condensada de gran tamaño, color restringido, precisión en los datos | Fotos recortadas con `cover`: aquí **se ven completas** (`contain` sobre fondo desenfocado de la misma foto) |

El informe sugería ocultar "Usado": no se hace (honestidad). Se mantiene "usado" en cada tarjeta y se añade la etiqueta amarilla
**"Pocas millas"** cuando el vehículo tiene menos de 5,000 millas.

### Principios
1. **Claridad antes que adorno.** Una acción principal por pantalla (hablar por WhatsApp). Texto corto, botones grandes.
2. **Celular primero.** La mayoría llega desde el teléfono (WhatsApp, Facebook). Todo funciona a 390 px (y a 320) sin scroll horizontal.
3. **El inventario manda.** Justo después del hero viene buscar y filtrar vehículos, antes de cualquier explicación.
4. **Honestidad.** Dato que falta = "por confirmar". Nunca inventar datos, reseñas ni número de dealers.
5. **Bilingüe real.** Cada pantalla existe en ES y EN, escrita de forma nativa (no traducción literal).
6. **Sin montos.** Ningún precio, inicial, mensualidad, APR ni plazo en el sitio, ni en nombres de archivo, ni en datos.

### Qué NO hacer
- Logos de marcas de autos (Chevrolet, GMC, Jeep, Kia…) como elemento de marca.
- Frases prohibidas (43 TAC §215.247): "financiamos a todos", "aprobación garantizada", "sin importar tu crédito", "everyone approved".
  Usar: "Muchos de nuestros dealers trabajan con ITIN, sin crédito o crédito dañado."
- Degradados morados, sombras en tarjetas o botones, ilustraciones genéricas, emojis como decoración, tarjetas idénticas sin jerarquía.
- Estilos o scripts **inline** (la CSP lo bloquea). Todo en `css/` y `js/`.
- Dependencias, frameworks o build. El sitio es HTML/CSS/JS plano.

## 2. Marca y logo

**Marca "puente":** dos letras C que se entrelazan (verde `#0F5A3C` a la izquierda, azul `#0E5AA7` a la derecha): comprador y dealers
unidos en una sola conversación. Geometría: dos arcos de radio 22, trazo 12, apertura de ±42°, centros a 33 de distancia, hueco de 2.6
en el cruce (el azul pasa por encima del verde arriba y el verde por encima del azul abajo). Verde y azul pasan a `#4CC486` / `#69AEF2`
sobre fondo oscuro. El logo lo diseñó Claude a pedido del dueño (oct 2026): si el dueño aporta uno oficial, se reemplazan los archivos
y los tokens `--accent*` de este documento.

| Archivo | Uso |
|---|---|
| `img/logo-mark.svg` | Marca sola en la cabecera (incluye su propia variante oscura vía `prefers-color-scheme`) |
| `img/logo-mark-dark.svg` | Marca sola sobre fondos siempre oscuros |
| `img/logo.svg`, `img/logo-dark.svg` | Versión completa "City Cars / Houston TX" (texto convertido a curvas); `logo-dark.svg` va en el pie |
| `favicon.svg`, `img/apple-touch-icon.png` (180), `img/logo-512.png` | Pestaña, pantalla de inicio del teléfono, JSON-LD |
| `tools/assets/logo-dark.png` | Solo para `tools/build-og.py` (imágenes para compartir) |

Reglas: altura mínima de la marca 24 px; área libre alrededor igual a media C; no recolorear, estirar ni añadir sombras. En la cabecera el
nombre va en HTML ("City Cars" en 700 y "Houston TX" en 500, ver §4), no dentro del SVG.

## 3. Color

Define siempre los colores como variables; nunca valores sueltos en componentes.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--ink` / `--ink-2` | `#262C2F` / `#161B1D` | igual | Superficies siempre oscuras: hero (fondo de respaldo), pie, franja "NO hacemos", barra de guardados |
| `--bg` | `#F5F5F0` | `#121618` | Fondo de página |
| `--surface` | `#FFFFFF` | `#1B2124` | Tarjetas, paneles, hoja de filtros |
| `--text` | `#262C2F` | `#EDF1EE` | Texto principal |
| `--muted` | `#4D575B` | `#A8B3B0` | Texto secundario |
| `--rule` | `#D8D9D0` | `#2F383B` | Bordes y divisores |
| `--soft` | `#ECECE5` | `#232B2E` | Chips de datos, hover del menú |
| `--accent` | `#0E5AA7` | `#2A74BD` | Azul de marca: botón principal, marcas de caso, números de "Cómo funciona" |
| `--accent-deep` | `#0B4A8A` | `#215FA0` | Hover del azul (siempre más oscuro) |
| `--accent-ink` | `#0E5AA7` | `#79B7F5` | Azul para **texto y bordes** sobre superficies (etiquetas de filtros activos, barra de progreso) |
| `--yellow` | `#F5B700` | igual | Señales: "Pocas millas", línea de carretera, iconos de la franja oscura |
| `--focus` | `#0E5AA7` | `#F5B700` | Anillo de foco; en zonas siempre oscuras (hero, pie, `.dark`, `.favbar`, visor) es amarillo |
| `--wa` / `--wa-deep` | `#0F7A40` / `#0B6A37` | igual | Verde **solo** para escribir por WhatsApp |
| `--ok` / `--warn` / `--err` | `#1C7446` / `#8A5300` / `#B42318` | `#4CC486` / `#F2B35A` / `#FF8A7A` | Estados |
| `--bar` | `rgba(255,255,255,.94)` | `rgba(27,33,36,.92)` | Fondo de la barra de cabecera |

El modo oscuro sigue solo `prefers-color-scheme` (no hay interruptor manual). **El verde es el color de WhatsApp y de nada más**: así
cada verde de la página significa "escríbenos". El azul es la marca; el amarillo es señal y **nunca** lleva texto blanco encima.

**Contraste calculado (WCAG):** blanco/`--wa` 5.4:1 · blanco/`--accent` 6.9:1 (oscuro 4.9:1; hover oscuro 6.5:1) · `--accent-ink`/`--surface` 6.9:1
(oscuro 7.7:1) · `--text`/`--bg` 12.9:1 · `--muted`/`--bg` 6.8:1 (oscuro 8.4:1) · `--ink`/`--yellow` (etiqueta) 7.9:1 · `--err` 6.0:1 · `--warn` 5.8:1 ·
`--ok` 5.3:1. Regla: texto normal ≥ 4.5:1, texto grande e interfaz ≥ 3:1. El anillo de foco amarillo sobre fondo claro daba 1.65:1: por eso
el foco es azul en claro y amarillo solo sobre oscuro.

**Texto sobre la foto del hero** (medido con capturas del hero sin texto: se toma el 5 % de píxeles más claros detrás de cada línea y se
calcula el contraste con el texto blanco y su opacidad): titular ≥ 4.6:1 en escritorio, 3.7:1 a 1024 px (texto grande, mínimo 3:1) y ≥ 6.2:1 en
celular (320–700 px); subtítulo, línea de respuesta y pie de foto ≥ 8:1 en todos los anchos. En celular el texto ocupa casi todo el hero y cae sobre el
capó claro, por eso hay un **velo anclado al bloque de texto** (`.hero-in::before`, ≤700 px) que crece con él. **Si cambias la foto, el texto
o el velo, vuelve a medir.**

## 4. Tipografía

- Fuente: **Instrument Sans** variable, autoalojada: un solo archivo `fonts/instrument-sans-var.woff2` (55 KB, licencia OFL en `fonts/OFL.txt`),
  `font-display: swap`. Ejes: peso 400–700 y **ancho 75–100 %** (`font-stretch`), que es lo que da el titular condensado estilo Porsche sin
  cargar otra familia. Pila de respaldo en `--font`.
- Cuerpo `1.0625rem / 1.55`, ancho 100 %. Titulares: **h1** peso 700, ancho 86 %, `line-height .97`, `letter-spacing -.016em`,
  `clamp(2.8rem, 10.8vw, 5.75rem)` · **h2** peso 700, ancho 88 %, `clamp(1.8rem, 4.2vw, 2.9rem)` · **h3** peso 650, ancho 94 %, `1.25rem`.
  Títulos de páginas internas (plan, "NO hacemos") `clamp(2rem, 4.6vw, 3.2rem)`; privacidad `clamp(2.2rem, 5.5vw, 3.2rem)`;
  ficha `clamp(2.1rem, 4.6vw, 3.3rem)`. `text-wrap: balance` en títulos.
- Cifras con `font-variant-numeric: tabular-nums` (millas, IDs, conteos) para que alineen.
- Ancho de línea cómodo: `.lead` 60ch, preguntas frecuentes 68ch, textos legales 95ch.

## 5. Espacio, forma y capas

- Radios: `--r-card: 14px` (tarjetas, paneles), `--r-ctl: 12px` (campos, avisos), píldora `999px` (botones, chips, buscador); barra de cabecera 18 px,
  hoja de filtros 20 px arriba.
- Contenedor `.wrap`: `width: min(1180px, 100% - 2rem)` (la barra de cabecera llega a 1240 px). Secciones: `padding: clamp(3rem, 6.5vw, 5.5rem) 0`.
- **Objetivos táctiles ≥ 44 px** (botones 52 px, chips 44–46, campos 52–54). Sin scroll horizontal a 390 px.
- Sombras solo donde algo flota (cabecera, menú móvil, paneles de filtros, botón flotante); nunca en tarjetas ni botones.
- Escala de capas (`z-index`): panel de filtro 35 · cabecera 40 · barra móvil 45 · botón flotante de WhatsApp 50 · enlace "saltar" 99 ·
  fondo oscuro de la hoja 110 · hoja de filtros 120 · visor de fotos 200.
- Puntos de corte: **960** (menú hamburguesa) · **900** (filtros pasan a hoja; plan, calculadora y trade-in a una columna) · 860 · 820 ("Cómo funciona"
  vertical, requisitos a una columna) · 800 · 760 (pie) · **700** (barra móvil, chips en una línea, velo del hero) · 560 (barra compacta, botón del hero a ancho
  completo) · 520 · 340.

## 6. Componentes

**Cabecera `.top > .bar`** — barra flotante (`position: fixed`, 10 px del borde) de vidrio (`backdrop-filter`), radio 18 px: marca, navegación, botón de
idioma (EN/ES) y botón verde de WhatsApp. En ≤ 960 px la navegación pasa a menú hamburguesa (`#nav-toggle`); en ≤ 560 px el botón de WhatsApp queda solo con el
icono y se oculta "Houston TX". Enlace activo con fondo `--soft`. Las páginas sin hero usan `body:not(.has-hero) main { padding-top: 84px }` para no quedar bajo la barra.

**Hero `.hero`** — `<picture>` (`img/hero-m.webp` hasta 700 px, `img/hero.webp` desde 701) con `fetchpriority="high"`; titular "Una conversación, muchos dealers.",
subtítulo para quien tiene mal crédito, sin crédito o solo ITIN/pasaporte, botón grande "Escríbenos por WhatsApp", enlace "Ver trocas y SUV", línea
"Te respondemos el mismo día…" y pie de foto "En la foto: <unidad>, ID <CCH-…>. Ver ficha" (lo escribe `build-inventory.py` entre `<!-- hero-caption -->`).
Línea amarilla `.dash` abajo. Entrada animada (foto que "asienta" y texto que sube, escalonado). En celular la barra inferior se oculta mientras el hero está en pantalla
(`body.hero-in-view`, `IntersectionObserver`), porque el botón de WhatsApp ya está arriba.

**Botones `.btn`** — píldora, alto 52 px (`.btn-sm` 44, `.btn-lg` 58), peso 650, sin sombras ni brillos. `.btn-wa` verde (contacto) · `.btn-primary` azul (acción de
marca) · `.btn-outline` borde (secundaria) · `.btn-light` blanco (sobre oscuro). Un botón dominante por zona; etiquetas cortas y en verbo.

**Chips `.chip`** — píldora con borde; elegido = fondo `--text` y texto `--bg` (`aria-pressed` o `aria-checked`). Sirven para el tipo de vehículo, los casos y las
preguntas rápidas de la ficha.

**¿Cuál es tu caso? `.casos`** — chips (en celular, una fila con scroll) y un panel `.case-panel` (borde izquierdo azul) cerrado al inicio: tocar un caso muestra su texto
y dos acciones, "Ver trocas y SUV" (filtra el inventario) y "Crear plan" (abre `plan/index.html?caso=<id>`).

**Selección de la portada** — sin filtros ni orden elegido, el inventario muestra solo **12 vehículos con varias marcas** (`FEATURED_N` en `js/app.js`): la mejor unidad de cada marca (año más nuevo y
menos millas) y, si hubiera menos marcas que tarjetas, la segunda mejor de cada una, de mejor a peor. Hoy son las 12 marcas del inventario, una cada una: «Mejores primero» se llenaba de GMC y Chevrolet
(más de la mitad del inventario; en las primeras 12 tarjetas solo salían 5 marcas). Sobre las tarjetas va «Una selección de 12 vehículos de 12 marcas. Tenemos 476 en total.» y debajo un botón azul
`.btn-primary` «Ver todo el inventario (476)», que deja las mismas 12 arriba y suma las siguientes (24 en total; luego «Ver 24 más») y guarda `?ver=todo` en la URL. Cualquier filtro, búsqueda u orden distinto de
«Mejores primero» muestra el inventario completo con paginación de 24, y al quitarlo vuelve la selección. En celular, «Ver N vehículos» de la hoja de filtros sin filtros también abre el inventario completo,
y un enlace `#<slug>` a una tarjeta fuera de la selección abre el inventario completo. Para cambiar el tamaño de la selección basta con `FEATURED_N`.

**Filtros del inventario** (sin precios, solo texto, solo lo que aplica a nuestros datos):
- *Escritorio (> 900 px):* barra superior `.fbar` arriba de los resultados: buscador grande (píldora con lupa) + "Ordenar por" (por omisión "Mejores primero": año más
  nuevo y, a igual año, menos millas); menús desplegables **Marca** (con conteos) · **Modelo** (desactivado hasta elegir marca) · **Año** (desde/hasta) · **Color** · **Millas** (máx.);
  y chips de tipo (Todos / Trocas / SUV / Sedanes / 3 filas / 4x4 confirmada). Cada menú (`.fdrop` + `.fpanel`) se cierra al elegir (menos Año), al hacer clic fuera, con Esc
  (devuelve el foco) o al salir con Tab.
- *Celular (≤ 900 px):* quedan buscador, "Filtros (n)" y "Ordenar por"; los grupos se abren como **hoja desde abajo** (pie con "Limpiar filtros" y "Ver N vehículos"; foco
  atrapado; Esc cierra). El grupo Modelo se oculta hasta elegir una marca (`.fgroup.no-make`).
- Sin iconos ni muestras de color en ninguna opción. Opciones `.fopt`: tocar la elegida la quita; el conteo respeta los demás filtros; opción en 0 queda deshabilitada.
- Filtros activos como etiquetas `.fchip` que se quitan con un toque + "Limpiar filtros". El estado vive en la URL con lista blanca
  (`?marca=&modelo=&desde=&hasta=&color=&millas=&orden=&tipo=&q=&ver=todo`), para que "Volver al inventario" desde una ficha conserve los filtros. Paginación de 24 en 24 en el inventario completo.

**Tarjeta de vehículo `.car`** — foto 4:3 **completa** (`.ph`, §8), etiqueta amarilla "Pocas millas" si tiene menos de 5,000 millas y corazón para guardar; debajo: título (enlace a
la ficha) con el ID a la derecha, "Color, usado", chips de datos (millas, tipo, 4x4 o 3 filas) y **un solo botón** "Preguntar por WhatsApp" alineado al fondo de la tarjeta.
No hay "Crear plan" ni "Ver ficha" sueltos: la foto y el título abren la ficha, y el plan se enlaza desde el menú, la barra móvil, los casos y la ficha. Hover/foco: el borde pasa a `--text`.

**Ficha del vehículo** (`es/carro/<slug>/`, `en/car/<slug>/`; estilos en `css/carro.css`, plantilla en `tools/build-inventory.py`) — contenedor de 1180 px. En ≥ 900 px dos
columnas: visor y miniaturas a la izquierda; a la derecha título, "Color, usado. ID", tres cifras grandes `.bigfacts` (Año · Millas · Tipo; "por confirmar" si falta el dato), el botón
principal **"Preguntar por WhatsApp"** (con icono; usa `--wa`), "Crear plan" / "Build my plan" (`.btn-outline`, a `plan/index.html?vehiculo=<slug>`) y tres preguntas rápidas en chips
(¿Sigue disponible? / ¿Qué opciones tengo? / Agendar visita; el mensaje de WhatsApp lleva el ID de la unidad). Debajo, "Se ve en las fotos" y, en dos columnas, datos generales y
especificaciones del modelo (`<th scope="row">`, con la nota "datos típicos del año/modelo, el dealer confirma la unidad"). El visor `.viewer` (4:3, fondo desenfocado de la propia foto)
abre a pantalla completa (`js/viewer.js`: pellizcar, arrastrar, doble toque, flechas, Esc).

**Crea tu plan** (`es/plan/`, `en/plan/`) — página propia, tres pasos con barra de progreso. Paso 1: si llega con `?vehiculo=` muestra la unidad elegida (`#chosen`, botón "Cambiar") y,
si no, un selector de tipo (Troca / SUV / Sedán / SUV de 3 filas / Todavía no decido). Al final arma un mensaje de WhatsApp (`new URL()` + `searchParams`) y un resumen que el cliente ve
antes de enviar. La pregunta de documentos es opcional y hay una casilla de consentimiento separada.

**Lo que NO hacemos** — página oscura (`body.page-dark`, franja `.dark` en `--ink`) con cuatro negaciones (iconos X amarillos) y el recuadro amarillo del WhatsApp oficial.

**Lo que sí hacemos `.trust`** — cuatro afirmaciones reales (`.proofs`, lista con filete superior) que viven de hechos ya existentes en el sitio. No hay reseñas, conteos ni logos de clientes: no
existen datos que respalden esas cosas. Solo se agrega una afirmación nueva si el dueño la confirma.

**Cómo funciona `.exits`** — cuatro "salidas" numeradas en cuadrados azules unidas por la línea amarilla de carretera (horizontal en escritorio, vertical en celular).

**Otros** — preguntas frecuentes con `<details>`; pie `--ink` con `logo-dark.svg`, horario, contacto y avisos legales; barra móvil `.mobilebar` (Crea tu plan + WhatsApp) en ≤ 700 px; botón
flotante de WhatsApp en escritorio; barra de guardados `.favbar`. No hay asistente de chat flotante (se eliminó por decisión del dueño).

## 7. Layout de la home (orden)

Cabecera flotante → **Hero** → **Inventario** (selección de 12 con varias marcas, filtros y «Ver todo») → ¿Cuál es tu caso? → Lo que sí hacemos → Cómo funciona → Requisitos → Calculadora (estimado educativo) →
Vende tu carro → Preguntas → Pie.
«Crea tu plan» y «Lo que NO hacemos» no están en la portada: son páginas propias (`/es/plan/`, `/en/plan/`, `/es/que-no-hacemos/`, `/en/what-we-dont-do/`); el menú enlaza al plan y el pie a «NO hacemos».
Los enlaces viejos `/es/#plan` y `/es/?vehiculo=` redirigen a la página del plan.

## 8. Fotos de vehículos

- Las fotos se ven **completas, sin recorte**: `object-fit: contain` sobre un fondo que es la misma foto desenfocada (`.ph::before { background: inherit; filter: blur() }`). Como la CSP
  prohíbe `style=""`, el `background-image` se asigna por CSSOM cuando carga la imagen (`photoLink()` en `js/app.js`, `fill()` en `js/viewer.js`).
- La **tarjeta muestra una sola foto**: la frontal (`portada` en el CSV). Todas las fotos se ven solo en la ficha. Las tres primeras tarjetas cargan sin `lazy`; el resto, `loading="lazy"`.
- Formato WebP en dos tamaños (`N-640.webp` tarjetas, `N-1200.webp` ficha y visor), `alt` descriptivo ("2026 Ram 1500 Rebel azul 1"). Los originales JPG no se publican.
- **Foto del hero:** `img/hero.webp` (1500×1167) sale de la foto 5 de `inventario-nuevo/2026-ram-1500-rebel-azul/` (CCH-526); `img/hero-m.webp` (780×1258) es un recorte vertical alrededor de
  la parrilla. La unidad se fija con `HERO_ID` en `tools/build-inventory.py`: si se da de baja, el generador se detiene para que elijas otra (y vuelvas a medir el contraste, §3).
- **Imágenes para compartir (WhatsApp, Facebook):** `img/og/<slug>.jpg` (1200×630, una por ficha, ≈45 MB en total) con `tools/build-og.py`; las de la portada (`img/og-es.jpg`, `img/og-en.jpg`)
  salen de la plantilla `tools/og-home.html` (reemplaza `{{H1}}` y `{{SUB}}` y captura 1200×630).
- Sin letreros de "financiado", montos, placas legibles ni caras. Si una foto los trae, pedir una limpia al dueño. **Si una foto no coincide con la ficha (otro color, otro vehículo), se corrige la
  etiqueta o se da de baja la unidad (`publicar=no`): nunca se deja la contradicción en pantalla.**

## 9. Movimiento

Solo dos cosas: la entrada del hero (la foto "asienta" en 1.8 s y el texto sube en 0.8 s, escalonado) y transiciones de color de 150–200 ms en botones, chips y bordes, más el giro de la
flecha de `<details>` y de los menús. Sin parallax, sin carruseles automáticos, sin aparición al hacer scroll. **Todo se desactiva con `prefers-reduced-motion: reduce`.**

## 10. Accesibilidad (obligatoria)

- Un solo `h1` por página, jerarquía de encabezados ordenada, enlace "Saltar al contenido", `lang` correcto.
- Todo control con nombre accesible (los radios del plan van dentro de su `<label>`); estados con `aria-pressed` / `aria-expanded` / `aria-live`; diálogos con `role="dialog"`, foco atrapado y
  foco devuelto al cerrar.
- **Foco visible:** contorno de 3 px con `--focus` (azul sobre claro, amarillo sobre oscuro). Campos de texto: borde `--accent-ink` + halo.
- Imágenes con `alt`; las decorativas, `alt=""`.
- Contraste según §3. Sin scroll horizontal a 320–390 px; funciona con zoom de texto.

## 11. Seguridad y plataforma (afecta al diseño)

- CSP estricta por cabecera en `vercel.json`: `style-src 'self'`, `script-src 'self'` → **sin `style=""` ni `<script>` inline**. Datos en `<script type="application/json">`. Cambios de estilo por JS solo vía CSSOM
  (`el.style.backgroundImage = …`). Solo las dos portadas llevan además una CSP en `<meta>`.
- Datos del usuario siempre con `textContent`; enlaces de WhatsApp con `new URL()` + `searchParams`; `rel="noopener noreferrer"`; `?vehiculo=` y `?caso=` con lista blanca.
- Nunca pedir Social ni depósitos por WhatsApp. Único WhatsApp oficial: (281) 602-7044.

## 12. Voz y contenido

- Español primero, inglés escrito de forma nativa. Tuteo, frases cortas, sin tecnicismos financieros.
- Modelo "puente": "Una conversación, muchos dealers" / "One conversation, many dealers".
- Aviso fijo: "City Cars Houston no es un concesionario ni un prestamista. Los vehículos los ofrecen y venden dealers con licencia en Texas. Aprobación, precio, inicial, APR y términos los decide el dealer o el financiador."
  (texto legal aprobado por el dueño; no reescribir).
- El aviso de marcas del pie se reescribió en el rediseño (antes nombraba cuatro marcas) y lleva la marca visible `[REVISAR CON ABOGADO]` hasta que el dueño lo confirme (ver el comentario en `tools/chrome.py`).
- Texto legal **nuevo** lleva la marca `[REVISAR CON ABOGADO]` hasta que el dueño lo confirme.

## 13. Cómo se construye (sin build, con tres generadores)

| Qué cambió | Qué correr |
|---|---|
| Inventario (`inventario-nuevo/inventario.csv`, fotos, especificaciones) | `python3 -I tools/build-inventory.py` → `js/vehicles.js`, las 476 fichas ES y EN y el pie de foto del hero |
| Menú, pie o avisos legales (`tools/chrome.py`) | `python3 -I tools/stamp-chrome.py` (las 8 páginas estáticas) y `python3 -I tools/build-inventory.py` (las fichas llevan la misma cabecera y pie) |
| Portadas o fotos (después de regenerar las fichas) | `python3 -I tools/build-og.py` (Pillow) |
| WebP de las fotos | `python3 -I tools/rebuild-webp.py`, luego `build-inventory.py` |

El cuerpo de las portadas, el plan, "NO hacemos" y privacidad se escribe a mano en su HTML; solo cabecera, pie y el pie de foto del hero se estampan.

## 14. Lista de revisión antes de publicar un cambio

- [ ] ¿Usa solo variables de color y las escalas de este documento? ¿El verde sigue siendo solo de WhatsApp?
- [ ] ¿Funciona a 390 px y a 1366 px, en ES y EN, en claro y en oscuro, sin errores de consola?
- [ ] ¿Objetivos táctiles ≥ 44 px, foco visible, contraste ≥ 4.5:1 (texto sobre foto medido, §3)?
- [ ] ¿Cero montos, cero frases prohibidas, cero logos de marcas?
- [ ] ¿Sin estilos/scripts inline? ¿Fotos completas (`contain`)? ¿Etiquetas de color y modelo coinciden con las fotos?
- [ ] ¿Regeneraste lo que corresponde (§13) y actualizaste `design.md` y `CLAUDE.md` si cambió un token o un componente?
