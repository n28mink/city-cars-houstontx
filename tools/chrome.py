"""Cabecera y pie compartidos de todas las páginas (ES/EN).

Una sola fuente: build-inventory.py la usa para las fichas y stamp-chrome.py
la estampa en las páginas estáticas (home, plan, "lo que no hacemos", privacidad).

Cada página se describe con:
  lang     "es" | "en"
  depth    niveles por debajo de es/ o en/  (0 = es/index.html, 1 = es/plan/, 2 = es/carro/<slug>/)
  current  "home" | "plan" | None  (marca el enlace activo del menú)
  alt_href ruta relativa a la misma página en el otro idioma
"""

WA_NUMBER = "12816027044"
WA_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/></svg>')
MENU_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h16M4 16h16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'

# El aviso de marcas (último párrafo de "legal") se reescribió en el rediseño de oct 2026: lleva la marca visible
# [REVISAR CON ABOGADO] hasta que el dueño lo confirme. Al aprobarlo, quita el <span class="flag"> de ES y EN y corre
# stamp-chrome.py y build-inventory.py.
T = {
    "es": dict(
        home_aria="City Cars Houston TX, inicio", menu="Abrir menú", main_aria="Principal",
        nav=[("Inventario", "index.html#inventario"), ("Requisitos", "index.html#requisitos"), ("Cómo funciona", "index.html#como-funciona"),
             ("Crea tu plan", "plan/index.html"), ("Preguntas", "index.html#preguntas")],
        lang_label="EN", lang_name="English", lang_code="en", lang_aria="English version", lang_hreflang="en",
        wa_aria="Escribir por WhatsApp", wa_text="WhatsApp",
        about="Una conversación, muchos dealers. Hablamos español e inglés.", wa_big="Escríbenos por WhatsApp",
        hours="Horario", hours_l1="Lunes a domingo", hours_l2="9:00 am – 8:00 pm",
        contact="Contacto", official="WhatsApp oficial: (281) 602-7044",
        nohacemos=("Lo que NO hacemos", "que-no-hacemos/index.html"), privacy=("Política de privacidad", "privacidad/index.html"),
        legal=["City Cars Houston TX no es un concesionario ni un prestamista. Los vehículos los ofrecen y venden dealers con licencia en Texas. Aprobación, precio, inicial, APR y términos los decide el dealer o el financiador.",
               "Nunca pedimos número de Social ni depósitos por WhatsApp. Nuestro único WhatsApp oficial es (281) 602-7044.",
               "Todas las marcas de vehículos mencionadas en este sitio son propiedad de sus respectivos dueños. City Cars Houston TX no está afiliado a ellas. <span class=\"flag\">[REVISAR CON ABOGADO]</span>"]),
    "en": dict(
        home_aria="City Cars Houston TX, home", menu="Open menu", main_aria="Main",
        nav=[("Inventory", "index.html#inventario"), ("Requirements", "index.html#requisitos"), ("How it works", "index.html#como-funciona"),
             ("Build your plan", "plan/index.html"), ("FAQ", "index.html#preguntas")],
        lang_label="ES", lang_name="Español", lang_code="es", lang_aria="Versión en español", lang_hreflang="es",
        wa_aria="Message us on WhatsApp", wa_text="WhatsApp",
        about="One conversation, many dealers. We speak English and Spanish.", wa_big="Message us on WhatsApp",
        hours="Hours", hours_l1="Monday to Sunday", hours_l2="9:00 am – 8:00 pm",
        contact="Contact", official="Official WhatsApp: (281) 602-7044",
        nohacemos=("What we don't do", "what-we-dont-do/index.html"), privacy=("Privacy policy", "privacy/index.html"),
        legal=["City Cars Houston TX is not a dealer or lender. All vehicles are offered and sold by licensed Texas dealers. Approval, price, down payment, APR and terms are set by the dealer or lender and depend on your credit and situation.",
               "We never ask for your Social Security number or a deposit on WhatsApp. Our only official WhatsApp is (281) 602-7044.",
               "All vehicle brands named on this site are trademarks of their respective owners. City Cars Houston TX is not affiliated with them. <span class=\"flag\">[REVISAR CON ABOGADO]</span>"]),
}


def _paths(depth):
    base = "../" * depth          # carpeta es/ o en/
    root = "../" * (depth + 1)    # raíz del sitio
    return base, root


def header(lang, depth, current=None, alt_href="#"):
    t = T[lang]; base, root = _paths(depth)
    links = []
    for label, href in t["nav"]:
        cur = (current == "plan" and href.startswith("plan/")) or (current == "home" and False)
        extra = ' aria-current="page"' if cur else ""
        links.append(f'<a href="{base}{href}"{extra}>{label}</a>')
    return f'''<header class="top">
  <div class="bar">
    <a class="brand" href="{base}index.html" aria-label="{t["home_aria"]}">
      <img class="brand-mark" src="{root}img/logo-mark.svg" width="46" height="36" alt="">
      <span class="brand-name"><b>City Cars</b><small>Houston TX</small></span>
    </a>
    <nav class="nav" id="nav" aria-label="{t["main_aria"]}">
      {chr(10).join("      " + l for l in links).strip()}
    </nav>
    <a class="lang" href="{alt_href}" hreflang="{t["lang_hreflang"]}" lang="{t["lang_code"]}" aria-label="{t["lang_aria"]}">{t["lang_label"]}</a>
    <a class="btn btn-wa btn-sm" data-wa href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener noreferrer" aria-label="{t["wa_aria"]}">{WA_SVG}<span>{t["wa_text"]}</span></a>
    <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="{t["menu"]}">{MENU_SVG}</button>
  </div>
</header>'''


def footer(lang, depth, alt_href="#"):
    t = T[lang]; base, root = _paths(depth)
    legal = "\n      ".join(f"<p>{p}</p>" for p in t["legal"])
    return f'''<footer id="contacto">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand-foot" href="{base}index.html" aria-label="{t["home_aria"]}"><img src="{root}img/logo-dark.svg" width="190" height="48" alt="City Cars Houston TX"></a>
        <p class="foot-about">{t["about"]}</p>
        <a class="btn btn-light" data-wa href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener noreferrer">{WA_SVG}{t["wa_big"]}</a>
      </div>
      <div>
        <h3>{t["hours"]}</h3>
        <ul><li>{t["hours_l1"]}</li><li>{t["hours_l2"]}</li></ul>
      </div>
      <div>
        <h3>{t["contact"]}</h3>
        <ul>
          <li>{t["official"]}</li>
          <li id="mail-slot"></li>
          <li><a href="{base}{t["nohacemos"][1]}">{t["nohacemos"][0]}</a></li>
          <li><a href="{base}{t["privacy"][1]}">{t["privacy"][0]}</a></li>
          <li><a href="{alt_href}" hreflang="{t["lang_hreflang"]}" lang="{t["lang_code"]}">{t["lang_name"]}</a></li>
        </ul>
      </div>
    </div>
    <div class="legal">
      {legal}
      <p>© <span id="year">2026</span> City Cars Houston TX.</p>
    </div>
  </div>
</footer>'''
