# design.md — City Cars Houston TX

Sistema de diseño del sitio. **Léelo antes de tocar HTML/CSS/JS** y úsalo como referencia para cualquier página o componente nuevo.
La fuente de verdad en código es `css/styles.css` (variables en `:root`); este documento explica el porqué y las reglas. Si cambias
un token o un componente, actualiza este archivo en el mismo commit.

## 1. Qué es esta marca

City Cars Houston TX es un **puente** entre compradores de Houston (hispanos y angloparlantes) y dealers con licencia en Texas.
**No es dealer ni prestamista.** El diseño debe sentirse **confiable, directo y local**: un letrero de autopista de Texas, no una
vitrina de lujo ni una plantilla genérica de IA.

Idea visual: **"letrero de autopista"** — verde de señal con borde blanco, líneas amarillas de carretera, asfalto oscuro.

### Principios
1. **Claridad antes que adorno.** Una acción principal por pantalla (hablar por WhatsApp). Texto corto, botones grandes.
2. **Celular primero.** La mayoría llega desde el teléfono (WhatsApp, Facebook). Todo debe funcionar a 390 px sin scroll horizontal.
3. **El inventario manda.** Lo primero de la home es buscar y filtrar vehículos, antes de cualquier texto.
4. **Honestidad.** Dato que falta = "por confirmar". Nunca inventar datos, reseñas ni número de dealers.
5. **Bilingüe real.** Cada pantalla existe en ES y EN, escrita de forma nativa (no traducción literal).
6. **Sin montos.** Ningún precio, inicial, mensualidad, APR ni plazo en el sitio, ni en nombres de archivo, ni en datos.

### Qué NO hacer
- Logos de marcas de autos (Chevrolet, GMC, Jeep, Kia…) como elemento de marca.
- Frases prohibidas (43 TAC §215.247): "financiamos a todos", "aprobación garantizada", "sin importar tu crédito", "everyone approved".
  Usar: "Muchos de nuestros dealers trabajan con ITIN, sin crédito o crédito dañado."
- Degradados morados, sombras exageradas, ilustraciones genéricas, emojis como decoración principal, tarjetas idénticas sin jerarquía.
- Estilos o scripts **inline** (la CSP lo bloquea). Todo en `css/` y `js/`.
- Dependencias, frameworks o build. El sitio es HTML/CSS/JS plano.

## 2. Color

| Token | Valor | Uso |
|---|---|---|
| `--sign` | `#0F5A3C` | Verde de letrero: cabecera, hero, botón principal secundario, estado "elegido" de chips/filtros, enlaces de marca |
| `--sign-deep` | `#0A452D` | Hover del verde |
| `--line` | `#F5B700` | Amarillo de carretera: acción principal, acentos, foco, líneas decorativas |
| `--asphalt` | `#262C2F` | Asfalto: franjas oscuras, barra inferior de fotos, carretera del hero |
| `--bg` | `#ECEFEA` | Fondo de página |
| `--surface` | `#FFFFFF` | Tarjetas, paneles |
| `--text` | `#1D2427` | Texto principal |
| `--muted` | `#4D575B` | Texto secundario |
| `--rule` | `#CFD5CF` | Bordes y divisores |
| `--soft` | `#DDE4DC` | Fondos suaves (etiquetas, botones circulares) |
| `--photo-bg` | `#F2F4F0` | Fondo detrás de las fotos (ver §7) |
| `--wa` | `#0F7A40` | Verde de WhatsApp (botón "Preguntar") |
| `--ok` / `--warn` / `--err` | `#1C7446` / `#8A5300` / `#B42318` | Estados |

**Modo oscuro** (`prefers-color-scheme: dark` y `data-theme="dark"`): `--bg #141A1C`, `--surface #1D2427`, `--text #EDF1EE`,
`--muted #A8B3B0`, `--rule #323B3E`, `--soft #243033`, `--photo-bg #1A2124`, `--asphalt #0E1213`, `--ok #4CC486`, `--warn #F2B35A`,
`--err #FF8A7A`. Define siempre los colores como variables; nunca valores sueltos en componentes (excepción: las muestras de color
del filtro `.sw-*`, que son datos).

**Contraste verificado (WCAG AA):** blanco/`--sign` 8.2:1 · blanco/`--wa` 5.4:1 · `--text`/`--line` 8.7:1 · `--muted`/`--bg` 6.4:1 ·
`--sign`/`--bg` 7.1:1 · `--warn`/`--bg` 5.5:1 · oscuro: `--muted`/`--bg` 8.2:1. Regla: texto normal ≥ 4.5:1, texto grande y
elementos de interfaz ≥ 3:1. El amarillo **nunca** lleva texto blanco (usa `--text`).

## 3. Tipografía

- Fuente: **Overpass**, autoalojada (`fonts/overpass-{400,600,800,900}.woff2`, `font-display: swap`). Pila de respaldo en `--font`.
- Cuerpo `1.0625rem` / interlineado `1.55`. Títulos con `line-height: 1.1`, peso 800–900, `letter-spacing` ligeramente negativo.
- Escala: h1 hero `clamp(2.4rem, 6vw, 4.4rem)` · h2 `clamp(1.8rem, 3.4vw, 2.6rem)` · h3 `1.25rem` · texto de apoyo `.88–.95rem`.
- Etiquetas pequeñas en mayúsculas (`text-transform: uppercase`, `letter-spacing: .04em`, peso 800) para encabezados de bloque
  dentro de tarjetas ("SE VE EN LAS FOTOS", "IDEAL PARA").
- Ancho de línea cómodo: párrafos `max-width` 48–68ch.

## 4. Espacio, forma y capas

- Radios: `--radius-s: 6px` (botones, campos), `--radius-m: 14px` (tarjetas, paneles), píldoras `999px` (chips, buscador).
- Contenedor `.wrap`: `width: min(1180px, 100% - 2rem)`. Gutter lateral mínimo de 16 px en celular.
- Separación vertical entre secciones: generosa (`clamp`), tarjetas con `gap: 1.25rem`.
- **Objetivos táctiles ≥ 44 px** (botones `min-height: 48px`, chips 44–46 px, campos 46–56 px).
- Sombras suaves y solo para elevar (hover de tarjeta, hoja de filtros). Sin bordes de color en todo.
- Escala de capas (`z-index`): contenido 0–3 · menú móvil 39 · cabecera 40 · barra móvil 45 · botón flotante de WhatsApp 50 ·
  enlace "saltar" 99 · fondo oscuro de hojas 110 · hoja de filtros 120 · visor de fotos 200.
- Puntos de corte usados: **960 · 900** (filtros pasan a hoja, hero a una columna) · 820 · 700 · 560 · 520 (cabecera compacta) · 480 · 360.

## 5. Componentes

**Cabecera `.top`** — sticky, fondo `--sign`, logo "puente" + nombre, navegación, botón de idioma (EN/ES) y botón blanco de WhatsApp.
En ≤ 960 px la navegación pasa a menú hamburguesa (`#nav-toggle`). Sombra al hacer scroll (`.scrolled`).

**Letrero del hero `.sign`** — bloque verde con borde interior blanco de 3 px y pestaña "Houston, TX"; debajo, la carretera `.road` con
líneas amarillas. En celular, el bloque "¿Por dónde quieres empezar?" (`.start`) va **arriba** del letrero (`order: -1`).

**Botones `.btn`** (alto 48 px, radio 6 px, peso 700; brillo que cruza al pasar el cursor):
- `.btn-primary` amarillo (acción principal, texto `--text`) · `.btn-sign` verde (secundaria de marca) · `.btn-wa` verde WhatsApp
  (contacto) · `.btn-ghost` borde gris (terciaria).
- Un solo botón amarillo o verde dominante por zona. Etiquetas cortas y en verbo: "Preguntar", "Crear plan", "Ver ficha".

**Chips `.chip`** — píldora con borde; estado elegido = fondo `--sign` + texto blanco (`aria-pressed="true"`). Se usan para el tipo de
vehículo (Todos / Trocas / SUV / Sedanes / 3 filas / 4x4) y los casos del cliente (`role="radio"`).

**Tarjeta de vehículo `.car`** — foto completa 3:2 (§7) con etiqueta de tipo arriba a la izquierda y corazón de guardado arriba a la
derecha; título (enlace a la ficha), color + ID, "año • millas", datos, "se ve en las fotos" (solo si hay datos), "Ideal para", y tres
acciones (Preguntar · Crear plan · Ver ficha). Hover/foco: se eleva 4 px y borde `--sign`.

**Filtros del inventario** (sin precios):
- *Escritorio (> 900 px):* columna fija a la izquierda (`.fside`, sticky) con grupos **Marca** (con conteos), **Modelo** (aparece al elegir
  marca), **Año** (desde/hasta), **Color** (muestras `.sw-*`) y **Millas** (máx.). A la derecha: buscador grande, "Ordenar por" y chips de tipo.
- *Celular (≤ 900 px):* la columna se convierte en **hoja desde abajo** (botón "Filtros (n)"; pie con "Limpiar filtros" y "Ver N vehículos";
  foco atrapado; Esc o fondo oscuro la cierran).
- Opciones `.fopt`: botón de una elección, tocar la elegida la quita; el conteo respeta los demás filtros; opción en 0 queda deshabilitada.
- Filtros activos como etiquetas `.fchip` que se quitan con un toque + "Limpiar filtros". El estado vive en la URL (lista blanca).

**Campos** — `input`/`select` de 46–56 px, borde 2 px `--rule`, foco con borde `--sign` y halo amarillo. Etiqueta visible siempre (clase `.sr`
solo si el contexto ya lo explica). Buscador con lupa dentro y forma de píldora.

**Ficha del vehículo** (`es/carro/<slug>/`, `en/car/<slug>/`, estilos en `css/carro.css`, plantilla en `tools/build-inventory.py`) —
contenedor de 1200 px. En ≥900 px, dos columnas: galería a la izquierda; a la derecha la etiqueta (`.eyebrow`: tipo · color · ID, 12 px/600
en mayúsculas con puntos amarillos), el título (44 px/800), la franja `.facts` con las cifras clave (Año · Millas · Tipo en 800; "Por
confirmar" en 600 gris si falta el dato), "Ideal para" con filete amarillo y los botones. En móvil el orden es título → galería → cifras →
botones. Debajo, con 96 px de aire (56 px en móvil), `.fx-more`: Datos generales y Especificaciones del modelo en dos columnas
(`<th scope="row">`, con nota "datos típicos, el dealer confirma la unidad") y "Se ve en las fotos" a todo el ancho.
Botones de la ficha (`.cta`): radio 10 px, relleno 14×28 px, peso 600. El primario es **siempre** "Preguntar por WhatsApp" / "Ask on
WhatsApp" con el icono SVG de WhatsApp (nunca un emoji ni solo "Preguntar") y usa `--wa`; el secundario es "Crear plan" / "Build my plan"
con borde, hacia la página del plan con el vehículo ya elegido (`plan/index.html?vehiculo=<slug>`). Una sola acción principal por ficha.

**Otros** — preguntas frecuentes con `<details>` y flecha verde; franja oscura `.dark` (asfalto) de la página "Lo que NO hacemos"; barra de guardados
`.favbar` verde; barra inferior móvil (`.mobilebar`: Crea tu plan + WhatsApp). No hay asistente de chat flotante (se eliminó por decisión del dueño).

## 6. Layout de la home (orden)

1. Cabecera → 2. **Inventario** (filtros + tarjetas) → 3. Hero (letrero + "¿Por dónde quieres empezar?") → 4. ¿Cuál es tu caso? →
5. Qué te piden normalmente → 6. Calculadora / Vende tu carro → 7. Cómo funciona → 8. Preguntas → Pie.
«Crea tu plan» y «Lo que NO hacemos» ya no están en la portada: son páginas propias (`/es/plan/`, `/en/plan/`, `/es/que-no-hacemos/`,
`/en/what-we-dont-do/`). El plan solo se enlaza desde el menú de arriba (y desde los botones «Crear plan» de tarjetas, casos y ficha, que
abren la misma página con `?vehiculo=` o `?caso=`); «Lo que NO hacemos» se enlaza desde el pie. Los avisos legales siguen en el pie de todas
las páginas. Los enlaces viejos `/es/#plan` y `/es/?vehiculo=` redirigen a la página del plan.
No hay franja de datos bajo el hero. El horario (todos los días, 9 am–8 pm) vive en el pie.

## 7. Fotos de vehículos

- Las fotos se ven **completas, sin recorte**: `object-fit: contain` sobre `--photo-bg` en tarjetas, galería y miniaturas.
- La **tarjeta muestra una sola foto**: la frontal (`portada` en el CSV). Todas las fotos se ven solo en la ficha.
- En la ficha, tocar la foto (o el botón de ampliar) abre el **visor de una foto**: pellizcar para acercar, arrastrar, doble toque/clic,
  rueda, flechas o deslizar para cambiar de foto, Esc para cerrar (`js/viewer.js`).
- Formato WebP en dos tamaños (`N-640.webp` tarjetas, `N-1200.webp` ficha/visor), `loading="lazy"`, `alt` descriptivo
  ("Chevrolet Silverado negro — vista delantera"). Los originales JPG no se publican.
- Sin letreros de "financiado", montos, placas legibles ni caras. Si una foto los trae, pedir una limpia al dueño.

## 8. Movimiento

Sutil y con propósito: aparición de secciones al entrar en pantalla, elevación de tarjetas, brillo de botones, giro de la flecha de
`<details>`. Duraciones 150–600 ms. **Todo se desactiva con `prefers-reduced-motion: reduce`.** Nada de animaciones que bloqueen la lectura.

## 9. Accesibilidad (obligatoria)

- Un solo `h1` por página, jerarquía de encabezados ordenada, enlace "Saltar al contenido", `lang` correcto.
- Todo control con nombre accesible; estados con `aria-pressed` / `aria-expanded` / `aria-live`; diálogos con `role="dialog"`, foco atrapado y
  foco devuelto al cerrar.
- Foco visible: contorno amarillo de 3 px (`:focus-visible`).
- Imágenes con `alt`; las decorativas, `aria-hidden`/`alt=""`.
- Sin scroll horizontal a 390 px; funciona con zoom de texto.

## 10. Seguridad y plataforma (afecta al diseño)

- CSP estricta: `style-src 'self'`, `script-src 'self'` → **sin `style=""` ni `<script>` inline**. Datos en `<script type="application/json">`.
  Cambios de estilo por JS solo vía CSSOM (`el.style.transform = …`).
- Datos del usuario siempre con `textContent`; enlaces de WhatsApp con `new URL()` + `searchParams`; `rel="noopener noreferrer"`.
- Nunca pedir Social ni depósitos por WhatsApp. Único WhatsApp oficial: (281) 602-7044.

## 11. Voz y contenido

- Español primero, inglés escrito de forma nativa. Tuteo, frases cortas, sin tecnicismos financieros.
- Modelo "puente": "Una conversación, muchos dealers" / "One conversation, many dealers".
- Aviso fijo: "City Cars Houston no es un concesionario ni un prestamista. Los vehículos los ofrecen y venden dealers con licencia en Texas.
  Aprobación, precio, inicial, APR y términos los decide el dealer o el financiador." (texto legal aprobado por el dueño; no reescribir).
- Texto legal **nuevo** lleva la marca `[REVISAR CON ABOGADO]` hasta que el dueño lo confirme.

## 12. Lista de revisión antes de publicar un cambio

- [ ] ¿Usa solo variables de color y las escalas de este documento?
- [ ] ¿Funciona a 390 px y a 1366 px, en ES y EN, sin errores de consola?
- [ ] ¿Objetivos táctiles ≥ 44 px, foco visible, contraste ≥ 4.5:1?
- [ ] ¿Cero montos, cero frases prohibidas, cero logos de marcas?
- [ ] ¿Sin estilos/scripts inline? ¿Fotos completas (`contain`)?
- [ ] ¿Actualizaste `design.md` y `CLAUDE.md` si cambió un token o un componente?
