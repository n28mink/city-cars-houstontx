#!/usr/bin/env python3
"""Importación ÚNICA (oct 2026) de las fotos con fondo blanco + el JSON de especificaciones.

Uso (desde la raíz del repo):
    python3 -I tools/import-fotos-blancas.py <especificaciones-vehiculos.json> <inventario-viejo.csv>

  <inventario-viejo.csv> es el CSV original (con `nombre_original`), que está en el historial de git
  (`git show dc1420f:inventario-nuevo/inventario.csv`): sirve para emparejar cada carpeta nueva con sus fotos normales.

Qué hace
  - Foto 1 = foto principal con fondo blanco (frontal), foto 2 = trasera con fondo blanco, y después las fotos normales
    originales (`inventario-nuevo/<carpeta>/N.jpg`). Genera los WebP 640/1200 en `inventario-nuevo-web/<carpeta>/`.
  - Reescribe `inventario-nuevo/inventario.csv` (sin montos) y crea `inventario-nuevo/especificaciones.json`.
  - NUNCA copia `down_payment_usd` ni nombres de carpeta con montos: los nombres se limpian antes de usarse.
Después corre `python3 -I tools/build-inventory.py` para regenerar `js/vehicles.js` y las fichas.
"""
import csv, json, os, re, sys, unicodedata
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
JSON_PATH, OLD_CSV = sys.argv[1], sys.argv[2]
WEB = "inventario-nuevo-web"

# Duplicados verificados a ojo (la misma unidad en dos carpetas): ids viejos y carpetas nuevas (índice en el JSON)
DUP_OLD = {f"CCH-{n:03d}" for n in (105, 27, 451, 102, 127, 277, 280, 489, 476, 215, 356, 367, 199, 269, 282, 287, 30, 238, 385, 373, 333, 437, 462, 516, 329)}
DUP_NEW_IDX = {298, 458}
# Color de las unidades nuevas (etiquetado a ojo sobre la foto con fondo blanco): índice en el JSON -> color
COLOR_NEW = {}
for col, idxs in {
    "blanco": "20 172 208 249 256 257 278 298 432 440 449 458 542 546 557 588",
    "negro": "25 366 407 427 443 477 482 500 512 513 525 528 529 569 584",
    "gris": "21 35 124 238 245 252 253 325 350 396 400 403 406 421 480 548",
    "plata": "5 31 43 45 57 174 305 454 488 552 558 577 589 594",
    "rojo": "70 152 265 336 338 416 422 466 495 504 508 547 556 561 565 570 502",
    "vinotinto": "34 95 186 487",
    "azul": "343 423 509 576 590",
    "celeste": "126 463 470",
    "marron": "108", "verde": "313 490 536", "beige": "424",
}.items():
    for i in idxs.split(): COLOR_NEW[int(i)] = col


def deaccent(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def clean_name(n):
    """Quita montos, millas y basura del nombre de carpeta del dealer."""
    s = n
    s = re.sub(r"\$?\s?\d[\d,\.]*\s?k?\s*(?:down\s*pay(?:ment|men)?|down|only\s*bank)\b", " ", s, flags=re.I)
    s = re.sub(r"\$\s?\d[\d,\.]*\s?k?(?:-\d+k?)?", " ", s)
    s = re.sub(r"\d[\d,\.]*\s?k?\s*(?:mil\s+)?(?:miles|millas)\b", " ", s, flags=re.I)
    s = re.sub(r"\bonly\s*bank\b", " ", s, flags=re.I)
    s = re.sub(r"\b\d{2,3}k\b", " ", s, flags=re.I)
    s = re.sub(r"\b\d{1,2}-(?=\s|$)", " ", s)
    s = re.sub(r"\bpaymen\b", " ", s, flags=re.I)
    s = re.sub(r"(?<=\d{4} )[A-Za-z] ", "", s)           # letras sueltas tras el año ("2023 R Chevy")
    s = s.replace(",", " ").replace("elevaton", "elevation")
    return re.sub(r"\s+", " ", s).strip()


def fmt_miles(n): return f"{int(n):,}" if n else ""


def miles_from_name(n):
    m = re.search(r"(\d[\d,\.]*)\s?k?\s*(?:mil\s+)?(?:miles|millas)", n, flags=re.I)
    if not m: m = re.search(r"\b(\d{2,3})k\b", n, flags=re.I)
    if not m: return ""
    txt = m.group(0).lower()
    num = float(m.group(1).replace(",", ""))
    return fmt_miles(num * 1000 if (num < 1000 and ("k" in txt or num < 400)) else num)


def webp(job):
    src, dst_dir, n = job
    if os.path.exists(f"{dst_dir}/{n}-1200.webp") and os.path.exists(f"{dst_dir}/{n}-640.webp"): return
    im = Image.open(src)
    if im.format == "JPEG": im.draft("RGB", (1500, 1500))  # decodifica reducido: mucho más rápido
    im = im.convert("RGB")
    for w in (640, 1200):
        t = im.copy()
        if t.width > w: t = t.resize((w, round(t.height * w / t.width)), Image.LANCZOS)
        t.save(f"{dst_dir}/{n}-{w}.webp", "WEBP", quality=78, method=4)


def main():
    data = json.load(open(JSON_PATH, encoding="utf-8"))["vehiculos"]
    old_rows = list(csv.DictReader(open(OLD_CSV, encoding="utf-8")))
    cur = {r["carpeta"]: r for r in csv.DictReader(open("inventario-nuevo/inventario.csv", encoding="utf-8"))}
    by_name = {r["nombre_original"]: (i, r) for i, r in enumerate(old_rows, 1)}
    json_by_old = {}
    new_items = []
    for idx, e in enumerate(data):
        if e["carpeta"] in by_name: json_by_old[by_name[e["carpeta"]][0]] = (idx, e)
        else: new_items.append((idx, e))

    out_rows, specs, used = [], {}, set(cur)
    nweb = 0

    def spec_of(e):
        s = e["especificaciones"]
        return {k: str(v) for k, v in {
            "motor": s["motor"], "caballos": s["caballos"], "torque": s["torque"], "transmision": s["transmision"],
            "traccion": s["traccion"], "mpg_ciudad": s["mpg_ciudad"], "mpg_autopista": s["mpg_autopista"],
            "combustible": s["combustible"], "remolque": s["remolque_max_lbs"], "asientos": s["asientos"], "carroceria": s["carroceria"]}.items()}

    jobs = []

    def build_photos(carpeta, whites, normals):  # solo registra los trabajos; se convierten en paralelo al final
        os.makedirs(f"{WEB}/{carpeta}", exist_ok=True)
        srcs = list(whites) + list(normals)
        for n, s in enumerate(srcs, 1): jobs.append((s, f"{WEB}/{carpeta}", n))
        return len(srcs)

    # --- vehículos que ya estaban (carpeta y id se conservan)
    for i, r in enumerate(old_rows, 1):
        vid = f"CCH-{i:03d}"
        row = dict(cur[r["carpeta"]]) if r["carpeta"] in cur else None
        assert row, r["carpeta"]
        hit = json_by_old.get(i)
        if not hit or vid in DUP_OLD:
            row.update(publicar="no", portada="1")
            out_rows.append(row); continue
        idx, e = hit
        nd = f"inventario-nuevo/{r['carpeta']}"
        normals = sorted((f for f in os.listdir(nd) if re.fullmatch(r"\d+\.(jpe?g|png|webp)", f, re.I)), key=lambda f: int(f.split(".")[0]))
        n = build_photos(r["carpeta"], e["fotos"], [f"{nd}/{f}" for f in normals])
        nweb += n
        row.update(num_fotos=str(n), portada="1", publicar="si")
        out_rows.append(row); specs[r["carpeta"]] = spec_of(e)

    # --- vehículos nuevos (solo fotos con fondo blanco)
    nid = len(old_rows)
    skipped = []
    for idx, e in new_items:
        if idx in DUP_NEW_IDX or not e["fotos"]:
            skipped.append(clean_name(e["carpeta"])); continue
        color = COLOR_NEW[idx]
        base = deaccent(clean_name(e["carpeta"])).lower()
        slug = re.sub(r"[^a-z0-9]+", "-", base).strip("-") + "-" + color
        s2, k = slug, 2
        while s2 in used: s2, k = f"{slug}-{k}", k + 1
        slug = s2; used.add(slug)
        nid += 1
        miles = fmt_miles(e["millas"]) if e["millas"] else miles_from_name(e["carpeta"])
        n = build_photos(slug, e["fotos"], [])
        nweb += n
        out_rows.append(dict(id=f"CCH-{nid:03d}", carpeta=slug, anio=e["año"], marca=e["marca"], modelo=clean_name(e["carpeta"]), tipo="", color=color,
                             millas=miles, num_fotos=str(n), portada="1", publicar="si"))
        specs[slug] = spec_of(e)

    from multiprocessing import Pool
    with Pool(os.cpu_count() or 2) as pool: pool.map(webp, jobs, chunksize=8)
    cols = ["id", "carpeta", "anio", "marca", "modelo", "tipo", "color", "millas", "num_fotos", "portada", "publicar"]
    with open("inventario-nuevo/inventario.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out_rows)
    json.dump(specs, open("inventario-nuevo/especificaciones.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    print("publicados:", sum(r["publicar"] == "si" for r in out_rows), "| nuevos:", len(new_items) - len(skipped), "| fotos WebP:", nweb)
    print("omitidos (duplicado o sin fotos):", skipped)


if __name__ == "__main__":
    main()
