"""Genera las imágenes para compartir de cada ficha (img/og/<slug>.jpg, 1200x630).

La foto de portada entra completa; el fondo es la misma foto desenfocada y el logo va abajo a la izquierda.
Se ejecuta después de build-inventory.py:  python3 -I tools/build-og.py
(Pillow). Las imágenes de la portada (img/og-es.jpg, img/og-en.jpg) salen de tools/og-home.html.
"""
import json, os, re, sys
from PIL import Image, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
W, H = 1200, 630
logo = Image.open("tools/assets/logo-dark.png").convert("RGBA")
logo.thumbnail((300, 76))
os.makedirs("img/og", exist_ok=True)

slugs = sorted(d for d in os.listdir("es/carro") if os.path.isfile(f"es/carro/{d}/index.html"))
keep = set()
for slug in slugs:
    html = open(f"es/carro/{slug}/index.html", encoding="utf-8").read()
    m = re.search(r'<script type="application/json" id="photos-data">(.*?)</script>', html, re.S)
    src = json.loads(m.group(1))[0]["src"]                      # ../../../inventario-nuevo-web/<carpeta>/N-1200.webp
    path = os.path.normpath(os.path.join(f"es/carro/{slug}", src.replace("%20", " "))) if "%" not in src else None
    if path is None:
        from urllib.parse import unquote
        path = os.path.normpath(os.path.join(f"es/carro/{slug}", unquote(src)))
    photo = Image.open(path).convert("RGB")
    # fondo: la misma foto, cubierta y desenfocada
    k = max(W / photo.width, H / photo.height)
    bg = photo.resize((round(photo.width * k), round(photo.height * k)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(26))).enhance(0.72)
    # primer plano: la foto completa
    f = min(W / photo.width, H / photo.height)
    fg = photo.resize((round(photo.width * f), round(photo.height * f)), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    # franja inferior suave y logo
    strip = Image.new("RGBA", (W, 150), (0, 0, 0, 0))
    px = strip.load()
    for y in range(150):
        a = int(170 * (y / 150) ** 1.6)
        for x in range(W): px[x, y] = (22, 27, 29, a)
    bg = bg.convert("RGBA"); bg.alpha_composite(strip, (0, H - 150)); bg.alpha_composite(logo, (36, H - logo.height - 26))
    bg.convert("RGB").save(f"img/og/{slug}.jpg", "JPEG", quality=70, optimize=True, progressive=True)
    keep.add(f"{slug}.jpg")
for f in os.listdir("img/og"):                                  # fichas dadas de baja: se borra su imagen
    if f not in keep: os.remove(f"img/og/{f}")
print(len(keep), "imágenes en img/og/")
