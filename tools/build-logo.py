"""Genera todos los archivos del logo de City Cars Houston TX.

LA MARCA (cuarta versión, oct 2026): «las dos C». Dos letras C entrelazadas —la inicial
de "City" y de "Cars"— en azul de marca, con relieve (degradado, brillo en el borde
superior y sombra suave) para que se lea como una ficha/insignia con volumen. Es un
regreso a la idea original del proyecto (la primera versión de todas, descartada por el
dueño por verse "demasiado abstracta, como joyería"): el dueño pidió retomarla ahora,
con un trazo más grueso y seguro —que se siga leyendo como dos C incluso a 16 px, el
tamaño del favicon— y con este tratamiento de relieve. El verde sigue sin aparecer en el
logo: en este sitio el verde significa solo "escríbenos por WhatsApp" (regla que no
cambió). El relieve es solo del logo: el resto del sitio sigue plano, sin sombras ni
degradados fuera de donde design.md ya los permite (cabecera, hoja de filtros, botón
flotante de WhatsApp).

Regenera los SVG:  python3 tools/build-logo.py       (necesita fontTools; el nombre
se convierte a trazos desde fonts/instrument-sans-var.woff2, así el SVG no depende
de ninguna fuente instalada).

Los PNG derivados (img/apple-touch-icon.png 180, img/logo-512.png 512 y
tools/assets/logo-dark.png, que usa build-og.py) se sacan abriendo estos SVG en un
navegador y capturando a ese tamaño; luego hay que volver a correr build-og.py.
"""
import math, os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

BLUE    = "#0E5AA7"   # azul de marca: tono base del relieve
BLUE_LT = "#2E86D4"   # azul claro: parte "iluminada" (arriba) del degradado
BLUE_DK = "#073E70"   # azul oscuro: solo para la sombra proyectada
HILITE  = "#BFE0FF"   # brillo del borde superior (bisel)
INK, MUTED = "#262C2F", "#4D575B"

# ---------------------------------------------------------------- la marca: dos C
R, STROKE = 26.0, 16.0        # radio exterior y grosor del trazo de cada C
INNER = R - STROKE
SEP   = 30.0                  # separación entre los centros de las dos C (crea el traslape)
GAP   = 64.0                  # grados de abertura de cada C
MARGIN = 6.0                  # aire alrededor para que no se recorte el brillo/la sombra
CX1, CX2 = R + MARGIN, R + MARGIN + SEP
CY = R + MARGIN
MW, MH = CX2 + R + MARGIN, 2 * (R + MARGIN)   # caja natural de la marca (más ancha que alta)

def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)

def _ring(cx, cy, r_out, r_in, gap_center, gap_deg):
    """Trazo de una C rellena: una dona con una abertura centrada en gap_center."""
    a0 = gap_center + gap_deg / 2
    a1 = a0 + (360 - gap_deg)
    large = 1 if (360 - gap_deg) > 180 else 0
    x0, y0 = _pt(cx, cy, r_out, a0); x1, y1 = _pt(cx, cy, r_out, a1)
    xi1, yi1 = _pt(cx, cy, r_in, a1); xi0, yi0 = _pt(cx, cy, r_in, a0)
    return (f'M{x0:.2f} {y0:.2f} A{r_out:.2f} {r_out:.2f} 0 {large} 0 {x1:.2f} {y1:.2f} '
            f'L{xi1:.2f} {yi1:.2f} A{r_in:.2f} {r_in:.2f} 0 {large} 1 {xi0:.2f} {yi0:.2f} Z')

def _rim(cx, cy, gap_center, gap_deg):
    """Arco delgado cerca del borde exterior de una C: el brillo del bisel."""
    rad = R - STROKE * 0.22
    a0 = gap_center + gap_deg / 2 + 10
    a1 = a0 + 140
    large = 1 if (a1 - a0) % 360 > 180 else 0
    x0, y0 = _pt(cx, cy, rad, a0); x1, y1 = _pt(cx, cy, rad, a1)
    return f'M{x0:.2f} {y0:.2f} A{rad:.2f} {rad:.2f} 0 {large} 0 {x1:.2f} {y1:.2f}'

def two_c_mark(uid):
    """Las dos C con relieve: degradado, brillo de bisel y sombra proyectada.
    Un solo tratamiento (sin variante clara/oscura): el degradado azul se lee bien
    tanto en superficies claras como oscuras gracias al propio volumen del relieve."""
    g, f, h1c, h2c = f"{uid}g", f"{uid}f", f"{uid}h1", f"{uid}h2"
    p1 = _ring(CX1, CY, R, INNER, 180, GAP)
    p2 = _ring(CX2, CY, R, INNER, 0, GAP)
    rim1 = _rim(CX1, CY, 180, GAP)
    rim2 = _rim(CX2, CY, 0, GAP)
    defs = (f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0.35" y2="1">'
            f'<stop offset="0" stop-color="{BLUE_LT}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>'
            f'<filter id="{f}" x="-40%" y="-40%" width="180%" height="180%">'
            f'<feDropShadow dx="0" dy="1.4" stdDeviation="1.3" flood-color="{BLUE_DK}" flood-opacity="0.45"/>'
            f'</filter></defs>')
    body = (f'<g filter="url(#{f})"><path d="{p1}" fill="url(#{g})"/><path d="{p2}" fill="url(#{g})"/></g>'
            f'<path d="{rim1}" fill="none" stroke="{HILITE}" stroke-width="2" stroke-linecap="round" opacity="0.55"/>'
            f'<path d="{rim2}" fill="none" stroke="{HILITE}" stroke-width="2" stroke-linecap="round" opacity="0.55"/>')
    return defs + body

# ---------------------------------------------------------------- el nombre
class Word:
    def __init__(self, font_path):
        self.base = TTFont(font_path)
    def paths(self, text, size, wght=700, wdth=100, track=0.0):
        f = instancer.instantiateVariableFont(self.base, {"wght": wght, "wdth": wdth}, inplace=False)
        upem = f["head"].unitsPerEm
        cmap = f.getBestCmap(); gs = f.getGlyphSet()
        hmtx = f["hmtx"]
        s = size / upem
        out, x = [], 0.0
        for ch in text:
            gn = cmap.get(ord(ch))
            if gn is None: x += size * 0.3; continue
            pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
            gs[gn].draw(TransformPen(pen, Transform(s, 0, 0, -s, x, 0)))
            d = pen.getCommands()
            if d: out.append(d)
            x += hmtx[gn][0] * s + track
        return " ".join(out), x - (track if text else 0)

# ---------------------------------------------------------------- composición
def lockup(word, c1, c2, uid):
    """marca (dos C) + «City Cars» / «Houston TX», alineados a la izquierda."""
    MH_L = 46.0                      # alto de la marca dentro del lockup
    k = MH_L / MH
    gap = 15.0
    d1, w1 = word.paths("City Cars",  30.0, wght=700, wdth=86, track=-0.35)
    d2, w2 = word.paths("Houston TX", 13.4, wght=500, wdth=100, track=1.05)
    tx = MW * k + gap
    H = 72.0
    y_mark = (H - MH_L) / 2
    b1, b2 = 40.0, 57.5              # líneas de base
    W = tx + max(w1, w2) + 1.5
    g = f'<g transform="translate(0 {y_mark:g}) scale({k:.4f})">{two_c_mark(uid)}</g>'
    t1 = f'<path transform="translate({tx:.2f} {b1:g})" d="{d1}" fill="{c1}"/>'
    t2 = f'<path transform="translate({tx:.2f} {b2:g})" d="{d2}" fill="{c2}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:g}" '
            f'role="img" aria-label="City Cars Houston TX">{g}{t1}{t2}</svg>')

def main(site):
    word = Word(os.path.join(site, "fonts/instrument-sans-var.woff2"))
    W = lambda p: os.path.join(site, p)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW:.1f} {MH:.1f}" role="img" aria-label="City Cars Houston TX">'
    # marca sola (cabecera): un solo tratamiento, se lee bien en claro y en oscuro
    open(W("img/logo-mark.svg"), "w").write(head + two_c_mark("cm") + "</svg>")
    # marca para superficies siempre oscuras (ícono de iPhone): mismo arte, mismo archivo
    open(W("img/logo-mark-dark.svg"), "w").write(head + two_c_mark("cd") + "</svg>")
    # favicon: la misma marca y caja que logo-mark.svg (más ancha que alta; no se fuerza a cuadrado)
    open(W("favicon.svg"), "w").write(head + two_c_mark("fv") + "</svg>")
    # lockup completo: texto oscuro sobre claro / texto claro sobre oscuro; la marca es la misma en los dos
    open(W("img/logo.svg"), "w").write(lockup(word, INK, MUTED, "ll"))
    open(W("img/logo-dark.svg"), "w").write(lockup(word, "#FFFFFF", "#C4CCCA", "ld"))
    print("SVG listos:", ", ".join(["img/logo-mark.svg", "img/logo-mark-dark.svg", "favicon.svg", "img/logo.svg", "img/logo-dark.svg"]))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
