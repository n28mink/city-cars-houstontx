"""Genera todos los archivos del logo de City Cars Houston TX.

LA MARCA (tercera versión, oct 2026): «el letrero». Una plancha de letrero de ruta
—la silueta de los letreros de carretera de EE.UU., con tapa plana y punta abajo—
en azul, con la línea central de una carretera (puntos que se angostan hacia el
vértice, como mirar la vía desde el letrero mismo) en amarillo. Retoma la
identidad "letrero de autopista de Texas" que el dueño ya había aprobado al
principio del proyecto, con una ejecución más sencilla y legible que las dos
versiones anteriores (las dos C entrelazadas; el puente en arco). El verde queda
libre para WhatsApp.

Regenera los SVG:  python3 tools/build-logo.py       (necesita fontTools; el nombre
se convierte a trazos desde fonts/instrument-sans-var.woff2, así el SVG no depende
de ninguna fuente instalada).

Los PNG derivados (img/apple-touch-icon.png 180, img/logo-512.png 512 y
tools/assets/logo-dark.png, que usa build-og.py) se sacan abriendo estos SVG en un
navegador y capturando a ese tamaño; luego hay que volver a correr build-og.py.
"""
import os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

BLUE, BLUE_D = "#0E5AA7", "#6FB2F2"
YEL          = "#F5B700"
INK, MUTED   = "#262C2F", "#4D575B"

# ---------------------------------------------------------------- la marca
MW, MH = 64.0, 72.0          # caja natural de la marca (letrero: más alto que ancho)
RC = 5.5                     # radio de las dos esquinas de arriba
SIDE_Y = MH * 0.56           # alto de los lados rectos antes de cerrar en punta
N_DASH = 3                   # puntos de la línea central

def shield_path(w=MW, h=MH, rc=RC, side_y_ratio=0.56):
    side_y = h * side_y_ratio
    return (f'M{rc:g} 0 L{w-rc:g} 0 Q{w:g} 0 {w:g} {rc:g} '
            f'L{w:g} {side_y:.2f} L{w/2:g} {h:g} L0 {side_y:.2f} L0 {rc:g} Q0 0 {rc:g} 0 Z')

def road_dashes(w=MW, h=MH, n=N_DASH):
    """Puntos que se angostan hacia el vértice: la carretera alejándose."""
    cx = w / 2
    y0, y1 = h * 0.145, h * 0.80
    dh = (y1 - y0) / (n * 2 - 1)
    out = []
    for i in range(n):
        y = y0 + i * 2 * dh
        t = i / (n - 1)
        wline = w * (0.30 * (1 - t * 0.42))
        out.append(f'<rect x="{cx - wline/2:.2f}" y="{y:.2f}" width="{wline:.2f}" height="{dh:.2f}" '
                    f'rx="{wline*0.32:.2f}" fill="{YEL}"/>')
    return "".join(out)

def mark_svg(color, cls=None):
    """Grupo <g> con la marca; cls permite cambiar el color en modo oscuro."""
    c = f' class="{cls}"' if cls else ""
    return f'<g{c} fill="{color}"><path d="{shield_path()}"/></g>{road_dashes()}'

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
def lockup(word, mark_color, mark_cls, c1, c2, uid):
    """marca + «City Cars» / «Houston TX», alineados a la izquierda."""
    MH_L = 54.0                      # alto de la marca dentro del lockup
    k = MH_L / MH
    gap = 15.0
    d1, w1 = word.paths("City Cars",  30.0, wght=700, wdth=86, track=-0.35)
    d2, w2 = word.paths("Houston TX", 13.4, wght=500, wdth=100, track=1.05)
    tx = MW * k + gap
    H = 72.0
    y_mark = (H - MH_L) / 2
    b1, b2 = 40.0, 57.5              # líneas de base
    W = tx + max(w1, w2) + 1.5
    css = (f'<style>@media (prefers-color-scheme:dark){{.{uid}m{{fill:{BLUE_D}}}'
           f'.{uid}t{{fill:#FFF}}.{uid}u{{fill:#C4CCCA}}}}</style>') if mark_cls else ""
    g = f'<g transform="translate(0 {y_mark:g}) scale({k:.4f})">{mark_svg(mark_color, mark_cls and uid+"m")}</g>'
    t1 = f'<path class="{uid}t" transform="translate({tx:.2f} {b1:g})" d="{d1}" fill="{c1}"/>' if mark_cls else \
         f'<path transform="translate({tx:.2f} {b1:g})" d="{d1}" fill="{c1}"/>'
    t2 = f'<path class="{uid}u" transform="translate({tx:.2f} {b2:g})" d="{d2}" fill="{c2}"/>' if mark_cls else \
         f'<path transform="translate({tx:.2f} {b2:g})" d="{d2}" fill="{c2}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:g}" '
            f'role="img" aria-label="City Cars Houston TX">{css}{g}{t1}{t2}</svg>')

def main(site):
    word = Word(os.path.join(site, "fonts/instrument-sans-var.woff2"))
    W = lambda p: os.path.join(site, p)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW:g} {MH:g}" role="img" aria-label="City Cars Houston TX">'
    # marca suelta (cabecera): azul, y azul claro si el sistema está en oscuro
    open(W("img/logo-mark.svg"), "w").write(
        head + '<style>@media (prefers-color-scheme:dark){.cm{fill:' + BLUE_D + '}}</style>'
        + mark_svg(BLUE, "cm") + "</svg>")
    # marca para superficies siempre oscuras (pie, imágenes para compartir)
    open(W("img/logo-mark-dark.svg"), "w").write(head + mark_svg(BLUE_D) + "</svg>")
    # favicon: la misma marca y caja que logo-mark.svg (el letrero es más alto que ancho; un favicon
    # cuadrado lo recortaría, así que se deja con su proporción natural, como logo-mark.svg)
    open(W("favicon.svg"), "w").write(
        head + '<style>@media (prefers-color-scheme:dark){.cm{fill:' + BLUE_D + '}}</style>'
        + mark_svg(BLUE, "cm") + "</svg>")
    # lockup completo
    open(W("img/logo.svg"), "w").write(lockup(word, BLUE, True, INK, MUTED, "ll"))
    open(W("img/logo-dark.svg"), "w").write(lockup(word, BLUE_D, False, "#FFFFFF", "#C4CCCA", "ld"))
    print("SVG listos:", ", ".join(["img/logo-mark.svg", "img/logo-mark-dark.svg", "favicon.svg", "img/logo.svg", "img/logo-dark.svg"]))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
