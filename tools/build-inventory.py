#!/usr/bin/env python3
"""Genera el inventario del sitio a partir de inventario-nuevo/inventario.csv.

Uso (desde la raíz del repo):  python3 -I tools/build-inventory.py

Produce:
  - js/vehicles.js                       (VEHICLES, formato compacto, ordenado "los mejores primero")
  - es/carro/<slug>/index.html           (una ficha por vehículo publicado, español)
  - en/car/<slug>/index.html             (una ficha por vehículo publicado, inglés)
  - inventario-nuevo/inventario.csv      (reescrito SIN columnas de montos)

Columnas editables del CSV:
  - publicar  "si"/"no": "no" da de baja el vehículo (no sale en el sitio). Además, solo se publican
              vehículos con año >= MIN_YEAR; si falta el año en la carpeta, se toma de la columna `anio`.
  - portada   número de la foto frontal que se muestra en la tarjeta (por defecto 1). La ficha del
              vehículo muestra todas las fotos, empezando por la portada.
  - anio / millas  se pueden corregir a mano (la carpeta manda para el año si lo trae).
Orden del sitio: año (más nuevo primero) y, a igual año, menos millas primero; sin millas al final.

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
MIN_YEAR = 2017  # decisión del dueño: solo se publican vehículos 2017 o más nuevos

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
TRUCK = {"silverado", "sierra", "f150", "tundra", "tacoma", "ram", "colorado", "canyon", "gladiator", "1500", "2500", "3500", "250", "350", "150", "f250", "f350", "titan"}
SUV = {"tahoe", "suburban", "yukon", "highlander", "rav4", "4runner", "pilot", "crv", "wrangler", "bronco",
       "expedition", "tucson", "trailblazer", "aviator", "durango", "compass", "wagoneer", "navigator"}
SEDAN = {"camry", "corolla", "civic", "accord", "altima", "charger", "300", "elantra"}
ROWS3 = {"tahoe", "suburban", "yukon", "expedition", "highlander", "pilot"}
ACRONYMS = {"slt", "sle", "lt", "ltz", "rst", "se", "xle", "xse", "sr", "sr5", "tss", "trd", "le", "xlt", "stx",
            "fx4", "at4", "at4x", "zr2", "z71", "gt", "sxt", "v6", "v8", "v4", "rt"}
FIXED = {"250": "F-250", "350": "F-350", "f250": "F-250", "f350": "F-350", "titan": "Titan", "150": "F-150", "crv": "CR-V", "rav4": "RAV4", "4runner": "4Runner", "f150": "F-150", "1500": "1500", "2500": "2500",
         "texas": "Texas", "edition": "Edition", "off": "Off", "road": "Road", "trail": "Trail", "boss": "Boss",
         "high": "High", "country": "Country", "king": "King", "ranch": "Ranch", "sport": "Sport", "touring": "Touring",
         "hatchback": "Hatchback", "denali": "Denali", "elevation": "Elevation", "premier": "Premier", "custom": "Custom",
         "platinum": "Platinum", "lariat": "Lariat", "limited": "Limited", "raptor": "Raptor", "rubicon": "Rubicon",
         "sahara": "Sahara", "mojave": "Mojave", "wildtrak": "Wildtrak", "heritage": "Heritage", "rebel": "Rebel",
         "adventure": "Adventure", "ultimate": "Ultimate", "max": "Max", "black": "Black", "diamond": "Diamond",
         "big": "Big", "horn": "Horn", "laramie": "Laramie", "ltz": "LTZ"}
# Erratas de las carpetas (palabras pegadas, cifras sueltas) -> palabras separadas, para que los modelos queden limpios
TOKFIX = {"slt4000": ["slt"], "suburbancon": ["suburban"], "2500laramie": ["2500", "laramie"],
          "elevation17k": ["elevation"], "denali2500": ["denali", "2500"]}
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
    fixed = []
    for i, t in enumerate(toks):
        if t in TOKFIX: fixed.extend(TOKFIX[t])
        elif t == "50" and i + 1 < len(toks) and toks[i + 1] == "v8": fixed.append("5.0")  # motor 5.0 V8
        else: fixed.append(t)
    toks = fixed
    year = toks[0] if re.fullmatch(r"(19|20)\d{2}", toks[0]) else ""
    if not year:
        m = re.search(r"\b(19|20)\d{2}\b", row.get("nombre_original", ""))
        year = m.group(0) if m else ""
    if not year and re.fullmatch(r"(19|20)\d{2}", (row.get("anio") or "").strip()):
        year = row["anio"].strip()
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


SPECS_PATH = "inventario-nuevo/especificaciones.json"
# Traducción ES -> EN de los textos de especificaciones (frases primero, palabras después)
EN_RULES = [
    (r"[Aa]utomática de (\d+), (\d+) o (\d+) velocidades", r"\1-, \2- or \3-speed automatic"),
    (r"[Aa]utomática (?:de )?(\d+), (\d+) o (\d+) velocidades", r"\1-, \2- or \3-speed automatic"),
    (r"[Aa]utomática (?:de )?(\d+) velocidades", r"\1-speed automatic"),
    (r"[Aa]utomática (?:de )?(\d+) o (\d+) velocidades", r"\1- or \2-speed automatic"),
    (r"(\d+) velocidades", r"\1-speed"), (r"[Aa]utomática", "automatic"), (r"[Mm]anual", "manual"),
    (r"varía según unidad", "varies by unit"), (r"varía según motor y tracción", "varies by engine and drivetrain"),
    (r"varía según motor", "varies by engine"), (r"varía según versión", "varies by trim"), (r"varía según", "varies by"),
    (r"según motor y configuración", "depending on engine and configuration"), (r"según motor y tracción", "depending on engine and drivetrain"),
    (r"según motor", "depending on engine"), (r"según unidad", "depending on unit"), (r"según versión", "depending on trim"), (r"según", "depending on"),
    (r"en algunas unidades", "on some units"), (r"algunas unidades", "some units"), (r"\bunidades\b", "units"), (r"\bunidad\b", "unit"),
    (r"\bestándar\b", "standard"), (r"\bEstándar\b", "Standard"), (r"\bopciones\b", "options"), (r"\bOpciones\b", "Options"),
    (r"\bopcional\b", "optional"), (r"\bopción\b", "option"), (r"\bdisponibles\b", "available"), (r"\bdisponible\b", "available"),
    (r"[Gg]asolina regular", "regular gasoline"), (r"[Gg]asolina", "gasoline"), (r"[Dd]iésel", "diesel"), (r"\bhíbrid[ao]\b", "hybrid"),
    (r"en variante", "in the"), (r"\bvariante\b", "variant"), (r"\bhasta\b", "up to"), (r"\bHasta\b", "Up to"), (r"\bmáximo\b", "max"),
    (r"lb-pie", "lb-ft"), (r"\bmás común\b", "most common"), (r"\bcomún\b", "common"), (r"\bmotor\b", "engine"), (r"\btracción\b", "drivetrain"),
    (r"\bversión\b", "trim"), (r"\btambién\b", "also"), (r"\bcon\b", "with"), (r"\bsin\b", "without"), (r"\bcilindros\b", "cylinders"),
    (r"(\d)-cil\b", r"\1-cyl"), (r"\bcabina doble\b", "double cab"), (r"\bcabina regular\b", "regular cab"), (r"\bcabina simple/doble\b", "regular/double cab"),
    (r"\bcabina simple\b", "regular cab"), (r"\bcabina extendida\b", "extended cab"), (r"camioneta", "truck"), (r"\bmediana\b", "midsize"),
    (r"\bSedán\b", "Sedan"), (r"SUV grande", "Large SUV"), (r"\bgrande\b", "large"), (r"\bpaquete\b", "package"), (r"\bsolo\b", "only"),
    (r"\bo\b", "or"), (r"\by\b", "and"), (r"\bde\b", "of"), (r"\ben\b", "in"), (r"\bel\b", "the"), (r"\bla\b", "the"), (r"\bes\b", "is"),
    (r"\bno\b", "not"), (r"\bmás\b", "more"), (r"\bbase\b", "base"), (r"\búnico\b", "only"), (r"\blote\b", "lot"),
]


EN_EXTRA = [(r"sin calificación oficial EPA", "official EPA rating not available"), (r"(?:camioneta )?de trabajo pesado", "heavy-duty"), (r"\bvaría\b", "varies"), (r"\bdoble cabina\b", "double cab"), (r"\bcabina\b", "cab"), (r"\bpesad[oa]\b", "heavy-duty"), (r"\bmás\b", "more"),
            (r"\bconfiguración\b", "configuration"), (r"\bambos\b", "both"), (r"\bsedán\b", "sedan"), (r"\bpor\b", "by"), (r"\bdel\b", "of the"),
            (r"\bhíbridas\b", "hybrid"), (r"\bpara\b", "for")]
# Si tras traducir queda español suelto (notas del investigador), se muestra solo lo anterior al primer paréntesis/;/—
ES_LEFT = re.compile(r"[áéíóúñ]|\b(?:este|esta|lote|mayoría|evalúa|vehículos?|trabajo|ambos|uso|línea|calificación|homologación|dinámico|tamaño|las|se)\b", re.I)


def en_spec(t):
    def tr(x):
        for a, b in EN_EXTRA + EN_RULES: x = re.sub(a, b, x, flags=re.I)
        return x
    out = tr(t)
    if ES_LEFT.search(out):
        short = re.split(r"\s\(|;|\s—", t)[0]
        out = tr(short)
    return out


def spec_rows(sp, lang):
    """Filas (etiqueta, valor) de la sección 'Especificaciones del modelo'. Solo texto del JSON, nunca montos."""
    es = lang == "es"
    # notas del investigador sobre "este lote" no son para el cliente: se quitan
    sp = {k: re.sub(r"\s*\([^)]*\b(?:lote|mayoría|evalúa|carpeta|nombre|la unidad|esta unidad)\b[^)]*\)", "", str(v)) for k, v in sp.items()}
    tr = (lambda x: x) if es else en_spec
    def num(x): return re.fullmatch(r"\d+", str(x).strip()) is not None
    out = []
    L = {"motor": ("Motor", "Engine"), "hp": ("Potencia", "Horsepower"), "tq": ("Torque", "Torque"), "tx": ("Transmisión", "Transmission"),
         "dr": ("Tracción del modelo", "Model drivetrain"), "mpg": ("Consumo (MPG)", "Fuel economy (MPG)"), "fuel": ("Combustible", "Fuel"),
         "tow": ("Remolque máximo", "Max towing"), "seats": ("Asientos", "Seats"), "body": ("Carrocería", "Body style")}
    def add(k, v):
        v = str(v or "").strip()
        if v: out.append((L[k][0 if es else 1], v))
    add("motor", tr(sp["motor"]))
    add("hp", tr(sp["caballos"]) + ("" if "hp" in sp["caballos"].lower() or not num(sp["caballos"]) else " hp"))
    add("tq", tr(sp["torque"]) + (" lb-pie" if es and num(sp["torque"]) else " lb-ft" if num(sp["torque"]) else ""))
    add("tx", tr(sp["transmision"]))
    add("dr", tr(sp["traccion"]))
    c, a = sp["mpg_ciudad"], sp["mpg_autopista"]
    if num(c) and num(a): add("mpg", (f"{c} ciudad / {a} carretera" if es else f"{c} city / {a} highway"))
    elif c == a: add("mpg", tr(c)[:1].upper() + tr(c)[1:])
    else: add("mpg", (("Ciudad: " if es else "City: ") + tr(c) + ". " + ("Carretera: " if es else "Highway: ") + tr(a)))
    add("fuel", tr(sp["combustible"]).capitalize())
    t = sp["remolque"]
    add("tow", f"{int(t):,} lb" if num(t) else tr(t))
    add("seats", tr(sp["asientos"]))
    add("body", tr(sp["carroceria"]))
    return out


def js_str(s): return json.dumps(s, ensure_ascii=False)


def main():
    rows = list(csv.DictReader(open(SRC_CSV, encoding="utf-8")))
    if "down_payment" not in rows[0]:
        # CSV ya saneado: reconstruimos desde columnas limpias
        for r in rows: r.setdefault("nombre_original", "")
    allitems, used = [], set()
    for k, r in enumerate(rows, 1):
        v = parse(r)
        n = int(r["num_fotos"])
        cover = int((r.get("portada") or "1").strip() or 1)
        assert 1 <= cover <= n, (v["carpeta"], cover, n)
        slug = deaccent(v["carpeta"]).lower()
        slug = re.sub(r"[^a-z0-9-]", "-", slug)
        assert slug not in used, slug
        used.add(slug)
        publish = (r.get("publicar") or "si").strip().lower() != "no" and bool(v["year"]) and int(v["year"]) >= MIN_YEAR
        if publish:
            files = [f"{WEB}/{v['carpeta']}/{i}-640.webp" for i in range(1, n + 1)]
            assert all(os.path.exists(f) for f in files), v["carpeta"]
        v.update(id=f"CCH-{k:03d}", slug=slug, n=n, cover=cover, publish=publish)
        allitems.append(v)

    def miles_num(v): return int(v["miles"].replace(",", "")) if v["miles"] else None
    # "Los mejores primero": año más nuevo y, a igual año, menos millas; sin millas al final.
    items = sorted((v for v in allitems if v["publish"]),
                   key=lambda v: (-int(v["year"]), miles_num(v) is None, miles_num(v) or 0, v["id"]))

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
    out.append("  // [id, slug, carpeta, año, marca, modelo, tipo, color, millas, nº fotos, 3 filas, tracción, extras, portada]")
    out.append("  var RAW = [")
    for r in items:
        out.append("    [" + ",".join([js_str(r["id"]), js_str(r["slug"]), js_str(r["carpeta"]), js_str(r["year"]), js_str(r["make"]),
                                       js_str(r["model"]), js_str(r["type"]), js_str(r["color"]), js_str(r["miles"]), str(r["n"]),
                                       "1" if r["rows3"] else "0", js_str(r["drive"] or ""), js_str(",".join(r["feats"])), str(r["cover"])]) + "],")
    out.append("  ];")
    out.append('''  window.VEHICLES = RAW.map(function (r, rank) {
    var seen = { es: [], en: [] };
    if (r[10] === "1") { seen.es.push("3 filas"); seen.en.push("3 rows"); }
    if (r[11]) { seen.es.push("4x4"); seen.en.push("4x4"); }
    r[12].split(",").forEach(function (f) { if (FEAT[f]) { seen.es.push(FEAT[f].es); seen.en.push(FEAT[f].en); } });
    var photos = [];
    for (var i = 1; i <= r[9]; i++) photos.push("@" + r[2] + "/" + i);
    return {
      id: r[0], slug: r[1], carpeta: r[2], year: r[3], make: r[4], model: r[5], type: r[6],
      yearNum: r[3] ? +r[3] : null, milesNum: r[8] ? +r[8].replace(/,/g, "") : null, rank: rank, cover: r[13] || 1,
      colorKey: r[7], color: { es: COLORS[r[7]][0], en: COLORS[r[7]][1] }, miles: r[8], condition: "used",
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
                   wa="Hola, me interesa el {t} ({id})", folder="carro", home="es",
                   specs_h="Especificaciones del modelo", specs_note="Datos típicos de este año y modelo, tomados de fuentes públicas (fabricante, KBB, Edmunds). El motor, la tracción y el equipamiento exactos de esta unidad los confirma el dealer."),
        "en": dict(lang="en", back="← Back to inventory", sub_tag="The bridge to dealers in Houston", gen="General",
                   year="Year", make="Make", model="Model", typ="Type", color="Color", miles="Mileage", seats="Seats", drive="Drivetrain",
                   types={"truck": "Truck", "suv": "SUV", "sedan": "Sedan"}, ideal_h="Great for", ask="📲 Ask about this vehicle",
                   tbc="To be confirmed", prev="Previous photo", next="Next photo", seen_h="Visible in the photos / from the listing name",
                   note="Year, mileage and features come from the inventory data; confirm this unit's exact details with the dealer. This sheet shows no prices: the dealer provides them in writing.",
                   wa="Hi, I'm interested in the {t} ({id})", folder="car", home="en",
                   specs_h="Model specifications", specs_note="Typical figures for this year and model, taken from public sources (manufacturer, KBB, Edmunds). The dealer confirms the exact engine, drivetrain and equipment of this unit."),
    }
    from html import escape as esc
    SPECS = json.load(open(SPECS_PATH, encoding="utf-8")) if os.path.exists(SPECS_PATH) else {}
    for v in items:
        for lang, T in TXT.items():
            ci = 0 if lang == "es" else 1
            title = f'{v["year"] or ""} {v["make"]} {v["model"]}'.strip()
            color = COLORS[v["color"]][ci]
            miles = (v["miles"] + (" millas" if lang == "es" else " miles")) if v["miles"] else T["tbc"]
            yr = v["year"] or T["tbc"]
            photos = []
            order = [v["cover"]] + [i for i in range(1, v["n"] + 1) if i != v["cover"]]  # la portada abre la galería
            for i in order:
                base = f"../../../{WEB}/{quote(v['carpeta'])}/{i}"
                photos.append({"src": f"{base}-1200.webp", "srcset": f"{base}-640.webp 640w, {base}-1200.webp 1200w", "alt": f"{title} {color.lower()} {len(photos) + 1}"})
            feats = [FEAT_TXT[f][ci] for f in v["feats"]]
            if v["drive"]: feats.insert(0, "4x4")
            if v["rows3"]: feats.insert(0, "3 filas" if lang == "es" else "3 rows")
            sp = SPECS.get(v["carpeta"])
            rows_ = [(T["year"], yr), (T["make"], v["make"]), (T["model"], v["model"] or T["tbc"]), (T["typ"], T["types"][v["type"]]),
                     (T["color"], color), (T["miles"], miles), (T["drive"], v["drive"] or T["tbc"])]
            if not sp: rows_.insert(6, (T["seats"], ("7 u 8" if lang == "es" else "7 or 8") if v["rows3"] else T["tbc"]))
            table = "".join(f'<tr><th scope="row">{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in rows_)
            spec_html = ""
            if sp:
                spec_html = (f'<h2>{T["specs_h"]}</h2><table>' + "".join(f'<tr><th scope="row">{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in spec_rows(sp, lang))
                             + f'</table><p class="note">{T["specs_note"]}</p>')
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
<a class="back" href="../../../{T["home"]}/#inventario">{T["back"]}</a>
<h1>{esc(title)}</h1>
<p class="sub">{esc(color)} • ID {v["id"]}</p>
<div class="viewer"><img id="vimg" src="{first["src"]}" srcset="{first["srcset"]}" alt="{esc(first["alt"])}"><button type="button" class="vnav prev" aria-label="{T["prev"]}">‹</button><button type="button" class="vnav next" aria-label="{T["next"]}">›</button><span class="vcount" id="vcount" aria-live="polite">1/{v["n"]}</span></div><div class="vthumbs" id="vthumbs"></div><script type="application/json" id="photos-data">{json.dumps(photos, ensure_ascii=False)}</script><script src="../../../js/viewer.js" defer></script>
<h2>{T["gen"]}</h2>
<table>{table}</table>
{spec_html}
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
        w.writerow(["id", "carpeta", "anio", "marca", "modelo", "tipo", "color", "millas", "num_fotos", "portada", "publicar"])
        for v in allitems:
            w.writerow([v["id"], v["carpeta"], v["year"], v["make"], v["model"], v["type"], v["color"], v["miles"], v["n"],
                        v["cover"], "si" if v["publish"] else "no"])

    # ---------------- resumen ----------------
    from collections import Counter
    print("vehículos publicados:", len(items), "| de baja:", len(allitems) - len(items))
    print("de baja:", [v["carpeta"] for v in allitems if not v["publish"]])
    print("portada distinta de 1:", sum(1 for v in items if v["cover"] != 1))
    print("tipos:", dict(Counter(v["type"] for v in items)))
    print("marcas:", dict(Counter(v["make"] for v in items)))
    print("sin año:", [v["carpeta"] for v in items if not v["year"]])
    print("sin millas:", sum(1 for v in items if not v["miles"]))
    print("sin modelo:", [v["carpeta"] for v in items if not v["model"]])
    print("muestra:", [f'{v["year"]} {v["make"]} {v["model"]} ({v["type"]})' for v in items[:6] + items[200:204] + items[-4:]])


if __name__ == "__main__":
    main()
