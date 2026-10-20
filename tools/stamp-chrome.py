"""Estampa la cabecera y el pie compartidos en las páginas estáticas.

Uso (desde la raíz del sitio):  python3 -I tools/stamp-chrome.py

Cada página lleva su cabecera entre  <!-- chrome:header -->…<!-- /chrome:header -->
y su pie entre  <!-- chrome:footer -->…<!-- /chrome:footer -->.  Si la página aún no
tiene marcas, se reemplaza el <header class="top"> / <footer> existente y se agregan.
Para cambiar el menú o el pie: edita tools/chrome.py y vuelve a correr este script.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chrome

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# archivo -> (idioma, profundidad, enlace activo, página equivalente en el otro idioma, relativa a esta página)
PAGES = {
    "es/index.html":                 ("es", 0, "home", "../en/index.html"),
    "en/index.html":                 ("en", 0, "home", "../es/index.html"),
    "es/plan/index.html":            ("es", 1, "plan", "../../en/plan/index.html"),
    "en/plan/index.html":            ("en", 1, "plan", "../../es/plan/index.html"),
    "es/que-no-hacemos/index.html":  ("es", 1, None,   "../../en/what-we-dont-do/index.html"),
    "en/what-we-dont-do/index.html": ("en", 1, None,   "../../es/que-no-hacemos/index.html"),
    "es/privacidad/index.html":      ("es", 1, None,   "../../en/privacy/index.html"),
    "en/privacy/index.html":         ("en", 1, None,   "../../es/privacidad/index.html"),
}


def swap(html, name, block, fallback_re):
    open_m, close_m = f"<!-- chrome:{name} -->", f"<!-- /chrome:{name} -->"
    wrapped = f"{open_m}\n{block}\n{close_m}"
    if open_m in html:
        return re.sub(re.escape(open_m) + r".*?" + re.escape(close_m), lambda m: wrapped, html, count=1, flags=re.S)
    new, n = re.subn(fallback_re, lambda m: wrapped, html, count=1, flags=re.S)
    if not n:
        raise SystemExit(f"No encontré dónde poner {name}")
    return new


def main():
    for rel, (lang, depth, current, alt) in PAGES.items():
        p = os.path.join(ROOT, rel)
        html = open(p, encoding="utf-8").read()
        html = swap(html, "header", chrome.header(lang, depth, current, alt), r'<header class="top">.*?</header>')
        html = swap(html, "footer", chrome.footer(lang, depth, alt), r'<footer[^>]*>.*?</footer>')
        open(p, "w", encoding="utf-8").write(html)
        print("ok", rel)


if __name__ == "__main__":
    main()
