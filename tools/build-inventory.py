#!/usr/bin/env python3
"""Genera el inventario del sitio a partir de inventario-nuevo/inventario.csv.

Uso (desde la raíz del repo):  python3 -I tools/build-inventory.py

Produce:
  - js/vehicles.js                       (VEHICLES, formato compacto)
  - es/carro/<slug>/index.html           (una ficha por vehículo, español)
  - en/car/<slug>/index.html             (una ficha por vehículo, inglés)
  - inventario-nuevo/inventario.csv      (reescrito SIN columnas de montos)

REGLA DEL DUEÑO: nunca montos (inicial, precio, mensualidad, APR, plazo). El CSV original traía
`down_payment` y `nombre_original` con montos: este script los lee solo para extraer año/millas/modelo
y NUNCA los escribe en ningún archivo.
"""
import csv, json, os, re, shutil, sys, unicodedata
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SRC_CSV = "inventario-nuevo/inventario.csv"
WEB = "inventario-nuevo-web"

COLORS = {  # clave del CSV -> (es, en)
    "gris": ("Gris", "Gray"), "negro": ("Negro", "Black"), "plata": ("Plata", "Silver"),
    "rojo": ("Rojo", "Red"), "azul": ("Azul", "Blue"), "vinotinto": ("Vinotinto", "Burgundy"),
    "celeste": ("Celeste", "Light blue"), "blanco": ("Blanco", "White"), "marron": ("Marrón", "Brown"),
    "dorado": ("Dorado", "Gold"), "morado": ("Morado", "Purple"), "verde": ("Verde", "Green"),
    "beige": ("Beige", "Beige"), "naranja": ("Naranja", "Orange"), "amarillo": ("Amarillo", "Yellow"),
}
MAKES = {"chevrolet": "Chevrolet", "chevy": "Chevrolet", "cherolet": "Chevrolet", "chevorlet": "Chevrolet",
         "gmc": "GMC", "ford": "Ford", "toyota": "Toyota", "dodge": "Dodge", "ram": "Ram", "honda": "Honda",
         "jeep": "Jeep", "chrysler": "Chrysler", "lincoln": "Lincoln", "hyundai": "Hyundai",
         "nissan": "Nissan", "kia": "Kia"}
JUNK = {"white", "gray", "grey", "blue", "black", "red", "silver", "g", "b"}
MODEL_MAKE = {  # marca inferida del modelo cuando la carpeta no la trae bien
    "silverado": "Chevrolet", "tahoe": "Chevrolet", "suburban": "Chevrolet", "colorado": "Chevrolet",
    "trailblazer": "Chevrolet", "sierra": "GMC", "yukon": "GMC", "canyon": "GMC", "f150": "Ford", "bronco": "Ford",
    "expedition": "Ford", "tundra": "Toyota", "tacoma": "Toyota", "rav4": "Toyota", "camry": "Toyota",
    "corolla": "Toyota", "highlander": "Toyota", "4runner": "Toyota", "ram": "Ram", "wrangler": "Jeep",
    "gladiator": "Jeep", "durango": "Dodge", "charger": "Dodge", "civic": "Honda", "accord": "Honda",
    "pilot": "Honda", "crv": "Honda", "aviator": "Lincoln", "tucson": "Hyundai", "altima": "Nissan",
}
TRUCK = {"silverado", "sierra", "f150", "tundra", "tacoma", "ram", "colorado", "canyon", "gladiator", "1500", "2500", "250", "150"}
SUV = {"tahoe", "suburban", "yukon", "highlander", "rav4", "4runner", "pilot", "crv", "wrangler", "bronco",
       "expedition", "tucson", "trailblazer", "aviator", "durango", "compass", "wagoneer", "navigator"}
SEDAN = {"camry", "corolla", "civic", "accord", "altima", "charger", "300", "elantra"}
ROWS3 = {"tahoe", "suburban", "yukon", "expedition", "highlander", "pilot"}
ACRONYMS = {"slt", "sle", "lt", "ltz", "rst", "se", "xle", "xse", "sr", "sr5", "tss", "trd", "le", "xlt", "stx",
            "fx4", "at4", "at4x", "zr2", "z71", "gt", "sxt", "v6", "v8", "v4", "rt"}
FIXED = {"crv": "CR-V", "rav4": "RAV4", "4runner": "4Runner", "f150": "F-150", "1500": "1500", "2500": "2500",
         "texas": "Texas", "edition": "Edition", "off": "Off", "road": "Road", "trail": "Trail", "boss": "Boss",
         "high": "High", "country": "Country", "king": "King", "ranch": "Ranch", "sport": "Sport", "touring": "Touring",
         "hatchback": "Hatchback", "denali": "Denali", "elevation": "Elevation", "premier": "Premier", "custom": "Custom",
         "platinum": "Platinum", "lariat": "Lariat", "limited": "Limited", "raptor": "Raptor", "rubicon": "Rubicon",
         "sahara": "Sahara", "mojave": "Mojave", "wildtrak": "Wildtrak", "heritage": "Heritage", "rebel": "Rebel",
         "adventure": "Adventure", "ultimate": "Ultimate", "max": "Max", "black": "Black", "diamond": "Diamond",
         "big": "Big", "horn": "Horn", "laramie": "Laramie", "ltz": "LTZ"}
# Palabras del nombre que pasan a "se ve / dato del nombre" en vez de formar parte del modelo
FEATURE_TOKENS = {"con", "quemacocos", "techo", "panorámico", "panoramico", "lifted", "diesel", "duramax", "motor",
                  "50", "5", "0", "4x4", "4wd", "awd"}


def deaccent(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def pretty_model(tokens):
    out, i = [], 0
    toks = list(tokens)
    while i < len(toks):
        t = toks[i]
        if t == "f" and i + 1 < len(toks) and toks[i + 1] == "150":  # f-150 -> F-150
            out.append("F-150"); i += 2; continue
        if t in FIXED: out.append(FIXED[t])
        elif t in ACRONYMS: out.append(t.upper())
        elif re.fullmatch(r"\d+", t): out.append(t)
        else: out.append(t.capitalize())
        i += 1
    return " ".join(out)


def fmt_miles(raw, nombre):
    raw = (raw or "").strip().lower()
    m = re.fullmatch(r"(\d{1,3})k", raw)
    if m: return f"{int(m.group(1)) * 1000:,}"
    if re.fullmatch(r"\d{3,6}", raw): return f"{int(raw):,}"
    if re.fullmatch(r"\d{1,3},\d{3}", raw): return raw
    n = re.search(r"(?<![\d$,])(\d{2,3})\s?k\b", (nombre or "").lower())
    if n: return f"{int(n.group(1)) * 1000:,}"
    n = re.search(r"(?<![\d$])(\d{2,3}),(\d{3})\s*(?:miles|millas|mi)", (nombre or "").lower())
    if n: return f"{int(n.group(1) + n.group(2)):,}"
    return ""


def parse(row):
    carpeta = row["carpeta"]
    toks = carpeta.split("-")
    if toks and re.fullmatch(r"\d{1,2}", toks[-1]) and len(toks) > 2: toks = toks[:-1]  # sufijo de duplicado
    year = toks[0] if re.fullmatch(r"(19|20)\d{2}", toks[0]) else ""
    if not year:
        m = re.search(r"\b(19|20)\d{2}\b", row.get("nombre_original", ""))
        year = m.group(0) if m else ""
    rest = toks[1:] if re.fullmatch(r"(19|20)\d{2}", toks[0]) else toks
    color_key = rest[-1] if rest and rest[-1] in COLORS else row["color"]
    if color_key not in COLORS: color_key = "gris"
    if rest and rest[-1] == color_key: rest = rest[:-1]
    make = None
    mid = []
    for t in rest:
        if t in MAKES and make is None or (t in MAKES and MAKES[t] == make): make = make or MAKES[t]; continue
        if t == "dodge" and make is None: make = "Dodge"; continue
        if t in MAKES and t in ("ram",): mid.append(t); continue
        mid.append(t)
    if "ram" in rest and (make is None or make == "Dodge"): make = "Ram"
    mid = [t for t in mid if t not in JUNK and t not in MAKES or t == "ram"]
    feats, model_toks = [], []
    j = 0
    while j < len(mid):
        t = mid[j]
        if t == "con" and j + 1 < len(mid) and mid[j + 1] == "quemacocos": feats.append("sunroof"); j += 2; continue
        if t == "quemacocos": feats.append("sunroof"); j += 1; continue
        if t == "techo": feats.append("pano"); j += 1; continue
        if t in ("panorámico", "panoramico"): j += 1; continue
        if t == "lifted": feats.append("lifted"); j += 1; continue
        if t in ("diesel", "duramax"):
            if "diesel" not in feats: feats.append("diesel")
            if t == "duramax": model_toks.append("Duramax") if False else None
            j += 1; continue
        if t == "motor": j += 1; continue
        model_toks.append(t); j += 1
    if make is None:
        for t in model_toks:
            if t in MODEL_MAKE: make = MODEL_MAKE[t]; break
        if make is None and row["marca"] in MAKES: make = MAKES[row["marca"]]
        make = make or "—"
    # el modelo no repite la marca ("gmc-sierra-slt" -> Sierra SLT)
    model_toks = [t for t in model_toks if t not in MAKES or t == "ram"]
    if make == "Ram" and model_toks[:1] == ["ram"]:
        model_toks = model_toks[1:]  # "Ram 1500" -> "1500"
        if not model_toks: model_toks = ["1500"]
    base = [t for t in model_toks]
    first = base[0] if base else ""
    key = re.sub(r"[^a-z0-9]", "", first)
    keys = {re.sub(r"[^a-z0-9]", "", t) for t in base} | {key}
    if make == "Ram" or "ram" in rest: vtype = "truck"
    elif keys & TRUCK: vtype = "truck"
    elif keys & SUV: vtype = "suv"
    elif keys & SEDAN: vtype = "sedan"
    else: vtype = "suv"
    rows3 = bool(keys & ROWS3)
    name = row.get("nombre_original", "").lower()
    drive = "4x4" if ("4x4" in name or "4wd" in name or keys & {"z71", "fx4", "rubicon", "at4", "at4x", "zr2", "trd", "raptor"}) else None
    if "4x4" in name or "4wd" in name: drive = "4x4"
    if "ram" in rest and not base: base = ["1500"]
    if len(base) > 1 and base[0] in ("1500", "2500", "250", "150") and base[1] in ("sierra", "silverado"):
        base = [base[1], base[0]] + base[2:]  # "1500 sierra slt" -> "Sierra 1500 SLT"
    model = pretty_model(base) or ("1500" if make == "Ram" else "")
    miles = fmt_miles(row.get("millas"), row.get("nombre_original"))
    return dict(carpeta=carpeta, year=year, make=make, model=model, type=vtype, rows3=rows3, drive=drive,
                color=color_key, miles=miles, feats=feats)


FEAT_TXT = {
    "sunroof": ("Quemacocos", "Sunroof"), "pano": ("Techo panorámico", "Panoramic roof"),
    "lifted": ("Elevada (lifted)", "Lifted"), "diesel": ("Motor diésel", "Diesel engine"),
}
IDEAL = {
    "truck": ("Para quien necesita una troca para trabajo y para el día a día.",
              "For anyone who needs a truck for work and everyday driving."),
    "suv": ("Para familias y para quien necesita espacio para pasajeros y maletas.",
            "For families and anyone who needs room for passengers and luggage."),
    "sedan": ("Para manejar todos los días en la ciudad.", "For everyday driving around town."),
}


def js_str(s): return json.dumps(s, ensure_ascii=False)


def main():
    rows = list(csv.DictReader(open(SRC_CSV, encoding="utf-8")))
    if "down_payment" not in rows[0]:
        # CSV ya saneado: reconstruimos desde columnas limpias
        for r in rows: r.setdefault("nombre_original", "")
    items, used = [], set()
    for k, r in enumerate(rows, 1):
        v = parse(r)
        n = int(r["num_fotos"])
        files = [f"{WEB}/{v['carpeta']}/{i}-640.webp" for i in range(1, n + 1)]
        assert all(os.path.exists(f) for f in files), v["carpeta"]
        slug = deaccent(v["carpeta"]).lower()
        slug = re.sub(r"[^a-z0-9-]", "-", slug)
        assert slug not in used, slug
        used.add(slug)
        v.update(id=f"CCH-{k:03d}", slug=slug, n=n)
        items.append(v)

    # ---------------- vehicles.js (compacto) ----------------
    colors = {k: list(c) for k, c in COLORS.items()}
    out = []
    out.append('// City Cars Houston TX — inventario de vehículos (GENERADO por tools/build-inventory.py).')
    out.append('// Para cambiar el inventario: edita inventario-nuevo/inventario.csv y vuelve a correr el script.')
    out.append('// Variable global VEHICLES; se carga antes de i18n.js y app.js.')
    out.append('// REGLA: nunca precios, inicial, mensualidad, APR ni plazos en este archivo.')
    out.append('"use strict";')
    out.append("(function () {")
    out.append("  var COLORS = " + json.dumps(colors, ensure_ascii=False) + ";")
    out.append("  var FEAT = " + json.dumps({k: {"es": a, "en": b} for k, (a, b) in FEAT_TXT.items()}, ensure_ascii=False) + ";")
    out.append("  var IDEAL = " + json.dumps({k: {"es": a, "en": b} for k, (a, b) in IDEAL.items()}, ensure_ascii=False) + ";")
    out.append("  var RAW = [")
    for r in items:
        out.append("    [" + ",".join([js_str(r["id"]), js_str(r["slug"]), js_str(r["carpeta"]), js_str(r["year"]), js_str(r["make"]),
                                       js_str(r["model"]), js_str(r["type"]), js_str(r["color"]), js_str(r["miles"]), str(r["n"]),
                                       "1" if r["rows3"] else "0", js_str(r["drive"] or ""), js_str(",".join(r["feats"]))]) + "],")
    out.append("  ];")
    out.append('''  window.VEHICLES = RAW.map(function (r) {
    var seen = { es: [], en: [] };
    if (r[10] === "1") { seen.es.push("3 filas"); seen.en.push("3 rows"); }
    if (r[11]) { seen.es.push("4x4"); seen.en.push("4x4"); }
    r[12].split(",").forEach(function (f) { if (FEAT[f]) { seen.es.push(FEAT[f].es); seen.en.push(FEAT[f].en); } });
    var photos = [];
    for (var i = 1; i <= r[9]; i++) photos.push("@" + r[2] + "/" + i);
    return {
      id: r[0], slug: r[1], carpeta: r[2], year: r[3], make: r[4], model: r[5], type: r[6],
      color: { es: COLORS[r[7]][0], en: COLORS[r[7]][1] }, miles: r[8], condition: "used",
      seats: r[10] === "1" ? { es: "7 u 8 pasajeros", en: "7 or 8 seats" } : { es: "Pasajeros por confirmar", en: "Seats to be confirmed" },
      rows3: r[10] === "1", drive: r[11] || null, dealer: "", photos: photos, seen: seen, ideal: IDEAL[r[6]]
    };
  });
  // Texto de millas/año con "por confirmar" cuando el dato no está (no inventar).
  window.milesText = function (v, l) {
    return v.miles ? v.miles + (l === "en" ? " miles" : " millas") : (l === "en" ? "Miles to be confirmed" : "Millas por confirmar");
  };
  window.yearText = function (v, l) { return v.year || (l === "en" ? "Year to be confirmed" : "Año por confirmar"); };
})();''')
    open("js/vehicles.js", "w", encoding="utf-8").write("\n".join(out) + "\n")

    # ---------------- fichas individuales ----------------
    for d in ("es/carro", "en/car"):
        if os.path.isdir(d): shutil.rmtree(d)
    SVG = ('<svg width="34" height="34" viewBox="0 0 64 64" aria-hidden="true"><path d="M10 42h44" stroke="#F5B700" stroke-width="4.5" stroke-linecap="round"/>'
           '<path d="M18 42V28M46 42V28" stroke="#fff" stroke-width="4.5" stroke-linecap="round"/>'
           '<path d="M10 28c6-11 16-17 22-17s16 6 22 17" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/></svg>')
    TXT = {
        "es": dict(lang="es", back="← Volver al inventario", sub_tag="El puente que te conecta con dealers en Houston", gen="Datos generales",
                   year="Año", make="Marca", model="Modelo", typ="Tipo", color="Color", miles="Millas", seats="Asientos", drive="Tracción",
                   types={"truck": "Troca", "suv": "SUV", "sedan": "Sedán"}, ideal_h="Ideal para", ask="📲 Preguntar por este vehículo",
                   tbc="Por confirmar", prev="Foto anterior", next="Foto siguiente", seen_h="Se ve en las fotos / dato del nombre",
                   note="Año, millas y características salen de los datos del inventario; confirma los datos exactos de esta unidad con el dealer. Esta ficha no muestra precios: el dealer los da por escrito.",
                   wa="Hola, me interesa el {t} ({id})", folder="carro", home="es"),
        "en": dict(lang="en", back="← Back to inventory", sub_tag="The bridge to dealers in Houston", gen="General",
                   year="Year", make="Make", model="Model", typ="Type", color="Color", miles="Mileage", seats="Seats", drive="Drivetrain",
                   types={"truck": "Truck", "suv": "SUV", "sedan": "Sedan"}, ideal_h="Great for", ask="📲 Ask about this vehicle",
                   tbc="To be confirmed", prev="Previous photo", next="Next photo", seen_h="Visible in the photos / from the listing name",
                   note="Year, mileage and features come from the inventory data; confirm this unit's exact details with the dealer. This sheet shows no prices: the dealer provides them in writing.",
                   wa="Hi, I'm interested in the {t} ({id})", folder="car", home="en"),
    }
    from html import escape as esc
    for v in items:
        for lang, T in TXT.items():
            ci = 0 if lang == "es" else 1
            title = f'{v["year"] or ""} {v["make"]} {v["model"]}'.strip()
            color = COLORS[v["color"]][ci]
            miles = (v["miles"] + (" millas" if lang == "es" else " miles")) if v["miles"] else T["tbc"]
            yr = v["year"] or T["tbc"]
            photos = []
            for i in range(1, v["n"] + 1):
                base = f"../../../{WEB}/{quote(v['carpeta'])}/{i}"
                photos.append({"src": f"{base}-1200.webp", "srcset": f"{base}-640.webp 640w, {base}-1200.webp 1200w", "alt": f"{title} {color.lower()} {i}"})
            feats = [FEAT_TXT[f][ci] for f in v["feats"]]
            if v["drive"]: feats.insert(0, "4x4")
            if v["rows3"]: feats.insert(0, "3 filas" if lang == "es" else "3 rows")
            rows_ = [(T["year"], yr), (T["make"], v["make"]), (T["model"], v["model"] or T["tbc"]), (T["typ"], T["types"][v["type"]]),
                     (T["color"], color), (T["miles"], miles), (T["seats"], ("7 u 8" if lang == "es" else "7 or 8") if v["rows3"] else T["tbc"]),
                     (T["drive"], v["drive"] or T["tbc"])]
            table = "".join(f'<tr><th scope="row">{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in rows_)
            seen = ("<h2>" + T["seen_h"] + "</h2><ul class=\"seen\">" + "".join(f"<li>{esc(f)}</li>" for f in feats) + "</ul>") if feats else ""
            waq = quote(T["wa"].format(t=title, id=v["id"]), safe="")
            desc = f'{title} — {color}, {miles}.'
            first = photos[0]
            page = f'''<!DOCTYPE html>
<html lang="{T["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | City Cars Houston TX</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="https://city-cars-houstontx.vercel.app/{T["home"]}/{T["folder"]}/{v["slug"]}/">
<link rel="icon" href="../../../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../../../css/assistant.css">
<link rel="stylesheet" href="../../../css/carro.css">
</head>
<body>
<header class="top">{SVG}<div><b>City Cars Houston TX</b><small>{T["sub_tag"]}</small></div></header>
<main class="wrap">
<a class="back" href="../../../{T["home"]}/">{T["back"]}</a>
<h1>{esc(title)}</h1>
<p class="sub">{esc(color)} • ID {v["id"]}</p>
<div class="viewer"><img id="vimg" src="{first["src"]}" srcset="{first["srcset"]}" alt="{esc(first["alt"])}"><button type="button" class="vnav prev" aria-label="{T["prev"]}">‹</button><button type="button" class="vnav next" aria-label="{T["next"]}">›</button><span class="vcount" id="vcount" aria-live="polite">1/{v["n"]}</span></div><div class="vthumbs" id="vthumbs"></div><script type="application/json" id="photos-data">{json.dumps(photos, ensure_ascii=False)}</script><script src="../../../js/viewer.js" defer></script>
<h2>{T["gen"]}</h2>
<table>{table}</table>
{seen}
<h2>{T["ideal_h"]}</h2>
<p class="ideal">{esc(IDEAL[v["type"]][ci])}</p>
<div class="cta"><a href="https://wa.me/12816027044?text={waq}" target="_blank" rel="noopener noreferrer">{T["ask"]}</a></div>
<p class="note">{T["note"]}</p>
</main>
<footer>City Cars Houston TX • Houston, TX • WhatsApp (281) 602-7044</footer>
<script src="../../../js/assistant.js"></script>
</body>
</html>
'''
            d = f"{lang}/{T['folder']}/{v['slug']}"
            os.makedirs(d, exist_ok=True)
            open(f"{d}/index.html", "w", encoding="utf-8").write(page)

    # ---------------- CSV saneado (sin montos) ----------------
    with open(SRC_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "carpeta", "anio", "marca", "modelo", "tipo", "color", "millas", "num_fotos"])
        for v in items:
            w.writerow([v["id"], v["carpeta"], v["year"], v["make"], v["model"], v["type"], v["color"], v["miles"], v["n"]])

    # ---------------- resumen ----------------
    from collections import Counter
    print("vehículos:", len(items))
    print("tipos:", dict(Counter(v["type"] for v in items)))
    print("marcas:", dict(Counter(v["make"] for v in items)))
    print("sin año:", [v["carpeta"] for v in items if not v["year"]])
    print("sin millas:", sum(1 for v in items if not v["miles"]))
    print("sin modelo:", [v["carpeta"] for v in items if not v["model"]])
    print("muestra:", [f'{v["year"]} {v["make"]} {v["model"]} ({v["type"]})' for v in items[:6] + items[200:204] + items[-4:]])


if __name__ == "__main__":
    main()
