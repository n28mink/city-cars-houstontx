"""Genera todos los archivos del logo de City Cars Houston TX.

LA MARCA: «el puente». Un tramo de carretera en arco que salva el vano sobre dos
pilas, con la raya amarilla siguiendo la curva. Es la palabra del negocio (el
puente entre el comprador y los dealers) dibujada con el mismo lenguaje de
carretera que ya usa el sitio. El verde queda libre para WhatsApp.

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

BLUE, BLUE_D = "#0E5AA7", "#6FB2F2"
YEL          = "#F5B700"
INK, MUTED   = "#262C2F", "#4D575B"
PAPER        = "#F5F5F0"

# ---------------------------------------------------------------- la marca
MW, MH = 72.0, 58.0          # caja natural de la marca
def _arc_y(cy, R, dx): return cy - math.sqrt(max(0.0, R*R - dx*dx))

def mark_parts(rise=9.0, apex=13.0, th=13.0, pier_w=9.0, ground=57.0):
    half = MW/2
    R  = (half*half + rise*rise)/(2*rise)
    cy = apex + R
    R2 = R - th
    yo, yi = _arc_y(cy, R, half), _arc_y(cy, R2, half)
    deck = (f'M0 {yo:.2f} A{R:.2f} {R:.2f} 0 0 1 {MW:g} {yo:.2f} '
            f'L{MW:g} {yi:.2f} A{R2:.2f} {R2:.2f} 0 0 0 0 {yi:.2f} Z')
    piers = []
    for px in (MW*0.235, MW*0.765):
        top = _arc_y(cy, R2, px-half) - .6
        piers.append(f'M{px-pier_w/2:.2f} {top:.2f} h{pier_w:g} '
                     f'l{pier_w*0.3:.2f} {ground-top:.2f} h{-pier_w*1.6:.2f} Z')
    Rc = R - th/2
    x0, x1 = 3.5, MW-3.5
    yc = _arc_y(cy, Rc, half-x0)
    line = f'M{x0:g} {yc:.2f} A{Rc:.2f} {Rc:.2f} 0 0 1 {x1:g} {yc:.2f}'
    return deck, piers, line

DECK, PIERS, LINE = mark_parts()

def mark_svg(color, cls=None, dx=0.0, dy=0.0):
    """Grupo <g> con la marca; cls permite cambiar el color en modo oscuro."""
    c = f' class="{cls}"' if cls else ""
    t = f' transform="translate({dx:g} {dy:g})"' if (dx or dy) else ""
    return (f'<g{t}><g{c} fill="{color}"><path d="{DECK}"/>'
            + "".join(f'<path d="{p}"/>' for p in PIERS) + "</g>"
            f'<path d="{LINE}" fill="none" stroke="{YEL}" stroke-width="4.2" '
            f'stroke-linecap="round" stroke-dasharray="9.5 8"/></g>')

# ---------------------------------------------------------------- el nombre
class Word:
    def __init__(self, font_path):
        self.base = TTFont(font_path)
    def paths(self, text, size, wght=700, wdth=100, track=0.0):
        f = instancer.instantiateVariableFont(self.base, {"wght": wght, "wdth": wdth}, inplace=False)
        upem = f["head"].unitsPerEm
        cmap = f.getBestCmap(); gs = f.getGlyphSet()
        hmtx = f["hmtx"]
        s = size/upem
        out, x = [], 0.0
        for ch in text:
            gn = cmap.get(ord(ch))
            if gn is None: x += size*0.3; continue
            pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
            gs[gn].draw(TransformPen(pen, Transform(s, 0, 0, -s, x, 0)))
            d = pen.getCommands()
            if d: out.append(d)
            x += hmtx[gn][0]*s + track
        return " ".join(out), x - (track if text else 0)

# ---------------------------------------------------------------- composición
def lockup(word, mark_color, mark_cls, c1, c2, uid):
    """marca + «City Cars» / «Houston TX», alineados a la izquierda."""
    MH_L = 54.0                      # alto de la marca dentro del lockup
    k = MH_L/MH
    gap = 15.0
    d1, w1 = word.paths("City Cars",  30.0, wght=700, wdth=86, track=-0.35)
    d2, w2 = word.paths("Houston TX", 13.4, wght=500, wdth=100, track=1.05)
    tx = MW*k + gap
    H = 72.0
    y_mark = (H - MH_L)/2
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
    # favicon: la marca centrada en un cuadrado
    open(W("favicon.svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW:g} {MW:g}" role="img" aria-label="City Cars Houston TX">'
        '<style>@media (prefers-color-scheme:dark){.cm{fill:' + BLUE_D + '}}</style>'
        + mark_svg(BLUE, "cm", dy=(MW-MH)/2) + "</svg>")
    # lockup completo
    open(W("img/logo.svg"), "w").write(lockup(word, BLUE, True, INK, MUTED, "ll"))
    open(W("img/logo-dark.svg"), "w").write(lockup(word, BLUE_D, False, "#FFFFFF", "#C4CCCA", "ld"))
    print("SVG listos:", ", ".join(["img/logo-mark.svg", "img/logo-mark-dark.svg", "favicon.svg", "img/logo.svg", "img/logo-dark.svg"]))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
