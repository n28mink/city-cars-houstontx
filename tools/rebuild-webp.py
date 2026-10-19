#!/usr/bin/env python3
"""Convierte las fotos originales de inventario-nuevo/<carpeta>/N.jpg a WebP 640 y 1200 px.

Uso (desde la raíz del repo):  python3 -I tools/rebuild-webp.py
Para cada vehículo con publicar=si en inventario-nuevo/inventario.csv genera
inventario-nuevo-web/<carpeta>/<n>-640.webp y <n>-1200.webp (mismo número que el archivo original) y actualiza
`num_fotos` con las fotos que realmente hay. Si el dueño reemplaza fotos con el mismo nombre, basta correr esto
y luego `python3 -I tools/build-inventory.py`.
"""
import csv, os, re
from multiprocessing import Pool
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SRC, WEB, CSV = "inventario-nuevo", "inventario-nuevo-web", "inventario-nuevo/inventario.csv"


def convert(job):
    src, dst, n = job
    im = Image.open(src)
    if im.format == "JPEG": im.draft("RGB", (1500, 1500))  # decodifica reducido: mucho más rápido
    im = im.convert("RGB")
    for w in (640, 1200):
        t = im.copy()
        if t.width > w: t = t.resize((w, round(t.height * w / t.width)), Image.LANCZOS)
        t.save(f"{dst}/{n}-{w}.webp", "WEBP", quality=78, method=4)


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    cols = list(rows[0].keys())
    jobs, changed = [], 0
    for r in rows:
        if r["publicar"] != "si": continue
        d = f"{SRC}/{r['carpeta']}"
        files = sorted((f for f in os.listdir(d) if re.fullmatch(r"\d+\.(jpe?g|png|webp)", f, re.I)), key=lambda f: int(f.split(".")[0]))
        dst = f"{WEB}/{r['carpeta']}"
        os.makedirs(dst, exist_ok=True)
        for f in files: jobs.append((f"{d}/{f}", dst, int(f.split(".")[0])))
        if str(len(files)) != r["num_fotos"]: r["num_fotos"] = str(len(files)); changed += 1
    with Pool(os.cpu_count() or 2) as pool: pool.map(convert, jobs, chunksize=8)
    with open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"{len(jobs)} fotos convertidas; {changed} vehículos con distinto nº de fotos")


if __name__ == "__main__":
    main()
