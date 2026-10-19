(function () {
  "use strict";

  // Anti-clickjacking: si la página está dentro de un iframe, salir de él.
  try { if (window.top !== window.self) window.top.location = window.self.location; } catch (e) { /* iframe cross-origin: no se puede salir */ }

  var LANG = document.documentElement.lang === "en" ? "en" : "es";

  // Raíz del sitio derivada de la ubicación de este script: funciona igual
  // en la raíz de un dominio, en un subdirectorio o en GitHub Pages.
  var SITE_ROOT = (function () {
    try {
      var cs = document.currentScript;
      if (cs && cs.src) return new URL(cs.src).href.replace(/\/js\/[^/]*$/, "");
    } catch (e) { /* se usa el fallback */ }
    return "";
  })();
  var IMG = SITE_ROOT + "/img/";
  var INV = SITE_ROOT + "/inventario-nuevo-web/";

  var CONFIG = {
    // Número armado por partes para dificultar el scraping. Único WhatsApp oficial: (281) 602-7044.
    whatsapp: ["1", "281", "602", "7044"].join(""),
    email: "" // Poner aquí el email de dominio (ej. "hola@tudominio.com"). Vacío = no se muestra.
  };

  // VEHICLES viene de js/vehicles.js; I18N viene de js/i18n.js (cargados antes que este script).
  var T = I18N[LANG];

  var HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.2-9.1C1.6 8.2 3.6 4.5 7.2 4.5c2 0 3.4 1 4.8 2.8 1.4-1.8 2.8-2.8 4.8-2.8 3.6 0 5.6 3.7 4.4 6.9-1.7 4.5-9.2 9.1-9.2 9.1Z" fill="none" stroke="currentColor" stroke-width="2"/></svg>';
  var ICON_OK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var ICON_INFO = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M12 7.5v6M12 16.6v.1" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>';

  // ---------- Utilidades seguras ----------
  function $(id) { return document.getElementById(id); }
  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) { if (Object.prototype.hasOwnProperty.call(attrs, k)) n.setAttribute(k, attrs[k]); }
    if (text != null) n.textContent = text;
    return n;
  }
  function icon(node, svg) { node.innerHTML = svg; return node; } // solo SVG estáticos de este archivo
  function clean(v, max) {
    return String(v == null ? "" : v).replace(/[\u0000-\u001F\u007F<>]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);
  }
  function waLink(text) {
    var u = new URL("https://wa.me/" + CONFIG.whatsapp);
    u.searchParams.set("text", String(text).slice(0, 1500)); // los datos del usuario ya pasaron por clean()
    return u.toString();
  }
  function store(key, val) {
    try {
      if (val === undefined) { var r = localStorage.getItem(key); return r ? JSON.parse(r) : null; }
      localStorage.setItem(key, JSON.stringify(val));
    } catch (e) { return null; }
    return null;
  }
  function fullName(v) { return v.make + " " + v.model; }
  function label(v) { return fullName(v) + " " + v.color[LANG].toLowerCase() + " (" + v.id + ")"; }
  // Lista blanca: solo acepta un slug o ID exacto del inventario
  function resolveVehicle(raw) {
    if (typeof raw !== "string" || !raw) return null;
    var s = raw.slice(0, 80).trim().toLowerCase();
    for (var i = 0; i < VEHICLES.length; i++) {
      if (VEHICLES[i].slug === s || VEHICLES[i].id.toLowerCase() === s) return VEHICLES[i];
    }
    return null;
  }

  // ---------- Enlaces de WhatsApp generales ----------
  document.querySelectorAll("[data-wa]").forEach(function (a) { a.href = waLink(T.waGeneral); });
  var yearEl = $("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
  var mailSlot = $("mail-slot");
  if (mailSlot) {
    if (CONFIG.email) { var m = el("a", null, CONFIG.email); m.href = "mailto:" + CONFIG.email; mailSlot.appendChild(m); }
    else mailSlot.remove();
  }

  // ---------- Menú móvil ----------
  var navToggle = $("nav-toggle"), navMenu = $("nav");
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", function () {
      var open = navMenu.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(open));
    });
    navMenu.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        navMenu.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  var grid = $("grid");
  if (!grid) return; // páginas de texto (privacidad, 404): no hay más que hacer
  document.body.classList.add("has-bar");

  // ---------- Casos ----------
  var caseChips = $("case-chips"), casePanel = $("case-panel");
  function showCase(c) {
    caseChips.querySelectorAll(".chip").forEach(function (b) { b.setAttribute("aria-checked", String(b.dataset.id === c.id)); });
    casePanel.textContent = "";
    casePanel.appendChild(el("p", null, c.text));
    var btn = el("button", { type: "button", "class": "btn btn-sign" }, c.action);
    btn.addEventListener("click", function () {
      if (c.plan) { setPerfil(c.id); goPlan(); }
      else { setFilter(c.filter); $("inventario").scrollIntoView(); }
    });
    casePanel.appendChild(btn);
  }
  T.cases.forEach(function (c) {
    var b = el("button", { type: "button", "class": "chip", role: "radio", "aria-checked": "false", "data-id": c.id }, c.label);
    b.addEventListener("click", function () { showCase(c); setPerfil(c.id); });
    caseChips.appendChild(b);
  });
  showCase(T.cases[0]);

  // ---------- Inventario ----------
  var favs = (store("cch:favs") || []).filter(function (s) { return resolveVehicle(s); });
  var filtersEl = $("filters");
  var PAGE = 24, shown = PAGE;
  var MILES_STEPS = [25000, 50000, 75000, 100000, 150000];

  function norm(t) { return String(t).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
  function uniq(list) { return list.filter(function (x, i) { return list.indexOf(x) === i; }); }
  function byText(a, b) { return a.localeCompare(b, LANG); }
  function thousands(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }

  // Datos derivados de cada vehículo: familia del modelo ("F-150 Lariat" -> "F-150") y texto de búsqueda
  var colorNames = {};
  VEHICLES.forEach(function (v) {
    v.family = v.model.split(" ")[0] || v.model;
    v.hay = norm([v.make, v.model, v.year, v.color[LANG], T.types[v.type], v.drive || "", v.id].join(" "));
    colorNames[v.colorKey] = v.color[LANG];
  });
  var MAKES = uniq(VEHICLES.map(function (v) { return v.make; })).sort(byText);
  var YEARS = uniq(VEHICLES.map(function (v) { return v.yearNum; }).filter(Boolean)).sort(function (a, b) { return b - a; });
  var COLOR_KEYS = Object.keys(colorNames).sort(function (a, b) { return byText(colorNames[a], colorNames[b]); });
  function famLabel(make, fam) { return make === "Ram" && /^\d/.test(fam) ? "Ram " + fam : fam; }

  function cmpMiles(a, b) {
    if (a.milesNum == null || b.milesNum == null) return a.milesNum == null ? (b.milesNum == null ? 0 : 1) : -1;
    return a.milesNum - b.milesNum;
  }
  var SORTS = {
    best: function (a, b) { return a.rank - b.rank; },  // orden de vehicles.js: año más nuevo y menos millas
    newest: function (a, b) { return (b.yearNum || 0) - (a.yearNum || 0) || cmpMiles(a, b) || a.rank - b.rank; },
    oldest: function (a, b) { return (a.yearNum || 9999) - (b.yearNum || 9999) || cmpMiles(a, b) || a.rank - b.rank; },
    miles: function (a, b) { return cmpMiles(a, b) || a.rank - b.rank; },
    az: function (a, b) { return byText(a.make + " " + a.model, b.make + " " + b.model) || (b.yearNum || 0) - (a.yearNum || 0) || a.rank - b.rank; }
  };

  // Estado de los filtros (también vive en la URL para poder volver desde una ficha o compartir la búsqueda)
  var F = { chip: "todos", q: "", make: "", model: "", from: "", to: "", color: "", miles: "", sort: "best" };
  var PARAM = { chip: "tipo", q: "q", make: "marca", model: "modelo", from: "desde", to: "hasta", color: "color", miles: "millas", sort: "orden" };
  var qWords = [];
  var ctl = { make: $("f-marca"), model: $("f-modelo"), from: $("f-desde"), to: $("f-hasta"), color: $("f-color"), miles: $("f-millas"), sort: $("f-orden"), q: $("q-inv") };
  var panelEl = $("fpanel"), summaryEl = $("fsummary"), clearBtn = $("f-clear"), chipsEl = $("fchips"), activeEl = $("factive");

  T.filters.forEach(function (f) {
    var b = el("button", { type: "button", "class": "chip", "aria-pressed": "false", "data-id": f[0] }, f[1]);
    b.addEventListener("click", function () { setFilter(f[0]); });
    filtersEl.appendChild(b);
  });
  function setFilter(id) { F.chip = id; refresh(); }

  function matches(v, skip) {  // skip: faceta que se ignora (para contar las opciones de esa misma lista)
    if (skip !== "q") { for (var qi = 0; qi < qWords.length; qi++) { if (v.hay.indexOf(qWords[qi]) < 0) return false; } }
    if (skip !== "chip" && F.chip !== "todos") {
      if (F.chip === "rows3") { if (!v.rows3) return false; }
      else if (F.chip === "4x4") { if (v.drive !== "4x4") return false; }
      else if (v.type !== F.chip) return false;
    }
    if (skip !== "make" && F.make && v.make !== F.make) return false;
    if (skip !== "model" && F.model && v.family !== F.model) return false;
    if (F.from && !(v.yearNum >= +F.from)) return false;
    if (F.to && !(v.yearNum <= +F.to)) return false;
    if (skip !== "color" && F.color && v.colorKey !== F.color) return false;
    if (F.miles && !(v.milesNum != null && v.milesNum <= +F.miles)) return false;  // sin millas confirmadas no entra en este filtro
    return true;
  }
  function countBy(skip, keyOf) {
    var c = {};
    VEHICLES.forEach(function (v) { if (matches(v, skip)) { var k = keyOf(v); c[k] = (c[k] || 0) + 1; } });
    return c;
  }
  function setOptions(sel, anyLabel, opts, counts, current) {
    sel.textContent = "";
    sel.appendChild(el("option", { value: "" }, anyLabel));
    opts.forEach(function (o) {
      var n = counts ? (counts[o.value] || 0) : null;
      var op = el("option", { value: o.value }, o.label + (n == null ? "" : " (" + n + ")"));
      if (n === 0 && o.value !== current) op.disabled = true;
      sel.appendChild(op);
    });
    sel.value = current;
  }
  // Opciones con conteos que respetan los demás filtros (la lista que cambió no se vuelve a armar)
  function syncPanel(except) {
    if (except !== "make") {
      setOptions(ctl.make, T.anyMake, MAKES.map(function (m) { return { value: m, label: m }; }), countBy("make", function (v) { return v.make; }), F.make);
    }
    if (except !== "model") {
      var fams = F.make ? uniq(VEHICLES.filter(function (v) { return v.make === F.make; }).map(function (v) { return v.family; })).sort(byText) : [];
      setOptions(ctl.model, F.make ? T.anyModel : T.pickMake, fams.map(function (f) { return { value: f, label: famLabel(F.make, f) }; }), F.make ? countBy("model", function (v) { return v.family; }) : null, F.model);
      ctl.model.disabled = !F.make;
    }
    if (except !== "color") {
      setOptions(ctl.color, T.anyColor, COLOR_KEYS.map(function (k) { return { value: k, label: colorNames[k] }; }), countBy("color", function (v) { return v.colorKey; }), F.color);
    }
  }
  function activeCount() {
    return ["q", "make", "model", "from", "to", "color", "miles"].filter(function (k) { return F[k]; }).length + (F.chip !== "todos" ? 1 : 0);
  }
  function panelCount() { return ["make", "model", "from", "to", "color", "miles"].filter(function (k) { return F[k]; }).length; }
  // Filtros activos como etiquetas que se quitan con un toque
  function activeLabels() {
    var out = [];
    if (F.chip !== "todos") T.filters.forEach(function (f) { if (f[0] === F.chip) out.push(["chip", f[1]]); });
    if (F.q) out.push(["q", "“" + F.q + "”"]);
    if (F.make) out.push(["make", F.make]);
    if (F.model) out.push(["model", famLabel(F.make, F.model)]);
    if (F.from) out.push(["from", T.fromLbl(F.from)]);
    if (F.to) out.push(["to", T.toLbl(F.to)]);
    if (F.color) out.push(["color", colorNames[F.color]]);
    if (F.miles) out.push(["miles", T.milesUpTo(thousands(F.miles))]);
    return out;
  }
  function syncChrome() {
    var n = panelCount();
    summaryEl.textContent = n ? T.panelN(n) : T.panel;
    filtersEl.querySelectorAll(".chip").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.id === F.chip)); });
    ctl.from.value = F.from; ctl.to.value = F.to; ctl.miles.value = F.miles; ctl.sort.value = F.sort;
    if (document.activeElement !== ctl.q) ctl.q.value = F.q;
    var labels = activeLabels();
    chipsEl.textContent = "";
    labels.forEach(function (l) {
      var li = el("li");
      var b = el("button", { type: "button", "class": "fchip", "aria-label": T.removeFilter + l[1] }, l[1] + " ×");
      b.addEventListener("click", function () {
        if (l[0] === "chip") F.chip = "todos"; else F[l[0]] = "";
        if (l[0] === "make") F.model = "";
        refresh();
      });
      li.appendChild(b); chipsEl.appendChild(li);
    });
    activeEl.hidden = labels.length === 0;
  }
  function saveState() {
    try {
      var u = new URL(window.location.href);
      Object.keys(PARAM).forEach(function (k) {
        var def = k === "chip" ? "todos" : k === "sort" ? "best" : "";
        if (F[k] && F[k] !== def) u.searchParams.set(PARAM[k], F[k]); else u.searchParams.delete(PARAM[k]);
      });
      window.history.replaceState(null, "", u.pathname + u.search + u.hash);
    } catch (e) { /* sin historial (p. ej. vista previa): los filtros siguen funcionando */ }
  }
  function loadState() {  // lista blanca: cada valor de la URL debe existir en el inventario
    var sp;
    try { sp = new URLSearchParams(window.location.search); } catch (e) { return; }
    function get(k) { return (sp.get(PARAM[k]) || "").slice(0, 60); }
    var chip = get("chip");
    T.filters.forEach(function (f) { if (f[0] === chip) F.chip = chip; });
    F.q = clean(get("q"), 60);
    MAKES.forEach(function (m) { if (norm(m) === norm(get("make"))) F.make = m; });
    if (F.make) VEHICLES.forEach(function (v) { if (v.make === F.make && norm(v.family) === norm(get("model"))) F.model = v.family; });
    ["from", "to"].forEach(function (k) { var y = +get(k); if (YEARS.indexOf(y) > -1) F[k] = String(y); });
    if (F.from && F.to && +F.to < +F.from) { var t = F.from; F.from = F.to; F.to = t; }
    var c = get("color");
    if (Object.prototype.hasOwnProperty.call(colorNames, c)) F.color = c;
    var mi = +get("miles");
    if (MILES_STEPS.indexOf(mi) > -1) F.miles = String(mi);
    var so = get("sort");
    if (Object.prototype.hasOwnProperty.call(SORTS, so)) F.sort = so;
  }
  function refresh(except) {
    shown = PAGE;
    qWords = norm(F.q).split(/\s+/).filter(Boolean);
    syncPanel(except); syncChrome(); saveState(); renderGrid();
  }

  // Listas fijas: años, millas y orden
  setOptions(ctl.from, T.anyYear, YEARS.map(function (y) { return { value: String(y), label: String(y) }; }), null, "");
  setOptions(ctl.to, T.anyYear, YEARS.map(function (y) { return { value: String(y), label: String(y) }; }), null, "");
  setOptions(ctl.miles, T.anyMiles, MILES_STEPS.map(function (m) { return { value: String(m), label: T.milesUpTo(thousands(m)) }; }), null, "");
  ctl.sort.textContent = "";
  T.sorts.forEach(function (s) { ctl.sort.appendChild(el("option", { value: s[0] }, s[1])); });

  ctl.make.addEventListener("change", function () { F.make = ctl.make.value; F.model = ""; refresh("make"); });
  ctl.model.addEventListener("change", function () { F.model = ctl.model.value; refresh("model"); });
  ctl.from.addEventListener("change", function () {
    F.from = ctl.from.value;
    if (F.from && F.to && +F.to < +F.from) F.to = F.from;
    refresh();
  });
  ctl.to.addEventListener("change", function () {
    F.to = ctl.to.value;
    if (F.from && F.to && +F.from > +F.to) F.from = F.to;
    refresh();
  });
  ctl.color.addEventListener("change", function () { F.color = ctl.color.value; refresh("color"); });
  ctl.miles.addEventListener("change", function () { F.miles = ctl.miles.value; refresh(); });
  ctl.sort.addEventListener("change", function () { F.sort = ctl.sort.value; refresh(); });
  ctl.q.addEventListener("input", function () { F.q = clean(ctl.q.value, 60); refresh(); });
  clearBtn.addEventListener("click", function () {
    F.chip = "todos"; F.q = ""; F.make = ""; F.model = ""; F.from = ""; F.to = ""; F.color = ""; F.miles = "";
    refresh();
    ctl.q.focus({ preventScroll: true });
  });

  function photoSrc(p, size) {
    // p: base local ("tahoe-rst-rojo-1") o URL externa (Drive). size: "640"|"1200".
    if (/^https?:\/\//i.test(p)) return { src: p, srcset: p };
    if (p.charAt(0) === "@") {  // "@carpeta/n": fotos WebP del inventario nuevo (inventario-nuevo-web/<carpeta>/<n>-640|1200.webp)
      var ip = p.slice(1).split("/"), ib = INV + encodeURIComponent(ip[0]) + "/" + ip[1];
      return { src: ib + "-" + size + ".webp", srcset: ib + "-640.webp 640w, " + ib + "-1200.webp 1200w" };
    }
    var base = IMG + p;
    return { src: base + "-" + size + ".webp", srcset: base + "-640.webp 640w, " + base + "-1200.webp 1200w" };
  }
  // La tarjeta muestra SOLO la foto frontal (portada); todas las fotos se ven en la ficha del vehículo.
  function cover(v, sheetUrl) {
    var g = el("div", { "class": "gallery" });
    var ph = photoSrc(v.photos[v.cover - 1] || v.photos[0], "640");
    var a = el("a", { "class": "cover", href: sheetUrl, tabindex: "-1", "aria-hidden": "true" });  // el título y "Ver ficha" ya son los enlaces accesibles
    a.appendChild(el("img", {
      src: ph.src,
      srcset: ph.srcset,
      sizes: "(max-width: 700px) 100vw, 400px",
      width: "640", height: "427", loading: "lazy", decoding: "async",
      alt: fullName(v) + " " + v.color[LANG].toLowerCase() + T.altFront
    }));
    g.appendChild(a);
    g.appendChild(el("span", { "class": "tag" }, T.types[v.type] + " • " + T.used));
    var fav = icon(el("button", { type: "button", "class": "fav", "aria-pressed": String(favs.indexOf(v.slug) > -1), "aria-label": T.save + fullName(v) }), HEART);
    fav.addEventListener("click", function () { toggleFav(v.slug, fav); });
    g.appendChild(fav);
    return g;
  }

  var moreBtn = $("more"), countEl = $("inv-count");
  if (!VEHICLES.length) {  // inventario en actualización: sin filtros ni tarjetas, solo el aviso
    document.querySelectorAll("#inventario .fbar, #fpanel, #factive").forEach(function (n) { n.hidden = true; });
    if (countEl) countEl.hidden = true;
  }
  function visibleList() { return VEHICLES.filter(function (v) { return matches(v); }).sort(SORTS[F.sort]); }
  function renderGrid(focusSlug) {
    grid.textContent = "";
    var list = visibleList();
    if (countEl) countEl.textContent = T.count(Math.min(shown, list.length), list.length);
    if (!list.length) { if (moreBtn) moreBtn.hidden = true; grid.appendChild(el("p", { "class": "lead" }, VEHICLES.length ? T.empty : T.soon)); return; }
    var hash = decodeURIComponent((window.location.hash || "").slice(1));  // enlace directo a una tarjeta lejana
    if (hash) { for (var hi = 0; hi < list.length; hi++) { if (list[hi].slug === hash && hi >= shown) { shown = Math.ceil((hi + 1) / PAGE) * PAGE; break; } } }
    list.slice(0, shown).forEach(function (v) {
      var card = el("article", { "class": "car", id: v.slug, "aria-label": fullName(v) });
      var sheetUrl = (LANG === "en" ? "car/" : "carro/") + v.slug + "/";
      card.appendChild(cover(v, sheetUrl));

      var body = el("div", { "class": "car-body" });
      var head = el("div");
      var h3 = el("h3", null);
      h3.appendChild(el("a", { href: sheetUrl }, fullName(v)));
      head.appendChild(h3);
      head.appendChild(el("p", { "class": "car-sub" }, v.color[LANG] + " • ID " + v.id));
      body.appendChild(head);

      var yl = el("p", { "class": "yearline" });
      yl.appendChild(el("span", null, yearText(v, LANG) + " • " + milesText(v, LANG)));
      body.appendChild(yl);

      var specs = el("ul", { "class": "specs" });
      [[v.seats[LANG], ""], [T.drive + ": ", v.drive || T.driveTbd], [T.types[v.type], ""]].forEach(function (s) {
        var li = el("li");
        if (s[1]) { li.appendChild(document.createTextNode(s[0])); li.appendChild(el("b", null, s[1])); }
        else li.appendChild(el("b", null, s[0]));
        specs.appendChild(li);
      });
      body.appendChild(specs);

      if (v.seen[LANG].length) {  // sin datos visibles no se muestra el bloque vacío
        var seen = el("div", { "class": "seen" });
        seen.appendChild(el("p", null, T.seen));
        var ul = el("ul");
        v.seen[LANG].forEach(function (f) { ul.appendChild(el("li", null, f)); });
        seen.appendChild(ul);
        body.appendChild(seen);
      }

      var ideal = el("p", { "class": "ideal" });
      ideal.appendChild(el("b", null, T.ideal));
      ideal.appendChild(document.createTextNode(v.ideal[LANG]));
      body.appendChild(ideal);
      body.appendChild(el("p", { "class": "dealer-line" }, v.dealer ? T.dealerNamed + v.dealer : T.dealerGeneric));

      var actions = el("div", { "class": "car-actions" });
      var ask = el("a", { "class": "btn btn-wa", target: "_blank", rel: "noopener noreferrer", "aria-label": T.ask + ": " + fullName(v) }, T.ask);
      ask.href = waLink(T.waCar(label(v)));
      var plan = el("button", { type: "button", "class": "btn btn-ghost", "aria-label": T.plan + ": " + fullName(v) }, T.plan);
      plan.addEventListener("click", function () { selectVehicle(v.slug); goPlan(); });
      var more = el("a", { "class": "btn btn-ghost", href: sheetUrl, "aria-label": T.fullSheet + ": " + fullName(v) }, T.fullSheet);
      actions.appendChild(ask); actions.appendChild(plan); actions.appendChild(more);
      body.appendChild(actions);
      card.appendChild(body);
      grid.appendChild(card);
    });
    if (moreBtn) {
      moreBtn.hidden = shown >= list.length;
      moreBtn.textContent = T.more(Math.min(PAGE, list.length - shown), list.length - shown);
    }
    if (focusSlug) { var fc = document.getElementById(focusSlug); var fl = fc && fc.querySelector("h3 a"); if (fl) fl.focus(); }
  }
  if (moreBtn) moreBtn.addEventListener("click", function () {
    var first = visibleList()[shown];
    shown += PAGE;
    renderGrid(first && first.slug);
  });
  function toggleFav(slug, btn) {
    var i = favs.indexOf(slug);
    if (i > -1) favs.splice(i, 1); else favs.push(slug);
    btn.setAttribute("aria-pressed", String(i === -1));
    store("cch:favs", favs);
    renderFavbar();
  }
  function renderFavbar() {
    var bar = $("favbar");
    if (!favs.length) { bar.classList.remove("show"); return; }
    var vs = favs.map(resolveVehicle);
    $("favtext").textContent = vs.length === 1 ? T.favOne + fullName(vs[0]) : T.favMany(vs.length);
    $("favlink").href = waLink(T.waFavs(vs.map(label).join(", ")));
    bar.classList.add("show");
  }
  loadState();
  panelEl.open = panelCount() > 0 || !window.matchMedia || window.matchMedia("(min-width: 701px)").matches;  // en el celular empieza cerrado
  refresh();
  renderFavbar();


  // ---------- Efectos de interfaz (sin librerías; respetan prefers-reduced-motion) ----------
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var topBar = document.querySelector(".top");
  if (topBar) {
    var onScroll = function () { topBar.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Resplandor que sigue al cursor sobre las tarjetas (delegación: las tarjetas se re-dibujan al filtrar)
  if (grid && !reduceMotion) {
    grid.addEventListener("pointermove", function (e) {
      var card = e.target.closest ? e.target.closest(".car") : null;
      if (!card) return;
      var r = card.getBoundingClientRect();
      card.style.setProperty("--mx", (e.clientX - r.left) + "px");
      card.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  }

  // Aparición suave de las secciones al entrar en pantalla
  if (!reduceMotion && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll("main > section:not(.hero):not(#inventario) > .wrap");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0 });
    targets.forEach(function (t) { t.classList.add("rv"); io.observe(t); });
    // Red de seguridad: si algo no se observó, no dejar contenido oculto
    window.setTimeout(function () { targets.forEach(function (t) { t.classList.add("in"); }); }, 4000);
  }

  // ---------- Crea tu plan ----------
  var form = $("planform"), steps = form.querySelectorAll(".step"), err = $("err");
  var current = 0;
  var selV = $("f-vehiculo");
  selV.appendChild(el("option", { value: "" }, T.undecided));
  VEHICLES.forEach(function (v) { selV.appendChild(el("option", { value: v.slug }, fullName(v) + " • " + v.color[LANG])); });
  function fillSelect(sel, list) {
    sel.appendChild(el("option", { value: "" }, T.choose));
    list.forEach(function (t, i) { sel.appendChild(el("option", { value: String(i) }, t)); });
  }

  function addOption(container, type, name, value, text) {
    var wrap = el("label", { "class": "opt" });
    var input = el("input", { type: type, name: name, value: value });
    wrap.appendChild(input); wrap.appendChild(el("span", null, text));
    container.appendChild(wrap);
    return input;
  }
  T.cases.forEach(function (c) { addOption($("opt-perfil"), "radio", "perfil", c.id, c.label); });
  T.docs.forEach(function (d) { addOption($("opt-docs"), "checkbox", "docs", d[0], d[1]); });

  function setPerfil(id) { form.querySelectorAll('input[name="perfil"]').forEach(function (r) { r.checked = r.value === id; }); }
  // Sincronizar los radios del plan con los chips de "¿Cuál es tu caso?" (y viceversa)
  form.querySelectorAll('input[name="perfil"]').forEach(function (r) {
    r.addEventListener("change", function () {
      var c = null;
      T.cases.forEach(function (x) { if (x.id === r.value) c = x; });
      if (c) showCase(c);
    });
  });
  function selectVehicle(slug) { var v = resolveVehicle(slug); selV.value = v ? v.slug : ""; }
  function goPlan() { $("result").hidden = true; form.hidden = false; showStep(0); $("plan").scrollIntoView(); }

  function showStep(n) {
    current = n;
    steps.forEach(function (s, i) { s.classList.toggle("active", i === n); });
    $("progress").querySelectorAll("li").forEach(function (li, i) {
      li.classList.toggle("done", i < n); li.classList.toggle("now", i === n);
    });
    $("back").classList.toggle("invisible", n === 0);
    $("next").textContent = n === steps.length - 1 ? T.lastBtn : T.nextBtn;
    err.textContent = "";
  }
  function checked(name) { var r = form.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : ""; }
  var NAME_RE = /^[A-Za-zÀ-ÖØ-öø-ÿÑñ' .-]{2,80}$/;

  function validate(n) {
    if (n === 2) {
      if (!NAME_RE.test(clean($("f-nombre").value, 80))) return { msg: T.errName, focus: $("f-nombre") };
      if (!NAME_RE.test(clean($("f-ciudad").value, 60))) return { msg: T.errCity, focus: $("f-ciudad") };
      if (!$("f-consent").checked) return { msg: T.errConsent, focus: $("f-consent") };
    }
    return null;
  }

  $("back").addEventListener("click", function () { if (current > 0) showStep(current - 1); });
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var problem = validate(current);
    if (problem) { err.textContent = problem.msg; if (problem.focus) problem.focus.focus(); return; }
    if (current < steps.length - 1) {
      showStep(current + 1);
      var f = steps[current].querySelector("input,select"); if (f) f.focus({ preventScroll: true });
      return;
    }
    buildPlan();
  });
  $("edit").addEventListener("click", function () { $("result").hidden = true; form.hidden = false; showStep(0); });

  function pick(list, raw) { var i = Number(raw); return raw !== "" && i >= 0 && i < list.length ? list[i] : ""; }

  function buildPlan() {
    var v = resolveVehicle(selV.value);
    var perfil = T.cases.filter(function (c) { return c.id === checked("perfil"); })[0];
    var docIds = Array.prototype.map.call(form.querySelectorAll('input[name="docs"]:checked'), function (i) { return i.value; });
    var docs = T.docs.filter(function (d) { return docIds.indexOf(d[0]) > -1; }).map(function (d) { return d[1]; });
    var share = $("f-share").checked;
    var nombre = clean($("f-nombre").value, 80), ciudad = clean($("f-ciudad").value, 60);

    var values = [
      v ? label(v) : T.undecided,
      perfil ? perfil.label : T.noCase,
      docs.length ? docs.join(", ") : T.noDocs,
      share ? T.yes : T.no
    ];
    var dl = $("ticket"); dl.textContent = "";
    values.forEach(function (val, i) { dl.appendChild(el("dt", null, T.rows[i])); dl.appendChild(el("dd", null, val)); });

    var notes = $("notes"); notes.textContent = "";
    function note(kind, text) {
      var n = icon(el("div", { "class": "note " + kind }), kind === "ok" ? ICON_OK : ICON_INFO);
      n.appendChild(el("span", null, text));
      notes.appendChild(n);
    }
    if (docIds.length && docIds.indexOf("id") < 0 && docIds.indexOf("alt") < 0) note("warn", T.noteNoId);
    if (!share) note("warn", T.noteShare);
    note("ok", T.noteDecide);

    var msg = T.msgHello(nombre, ciudad) + "\n" +
      values.map(function (val, i) { return "• " + T.msgRows[i] + ": " + val; }).join("\n") +
      "\n" + T.msgEnd;
    $("preview").textContent = msg;
    $("send").href = waLink(msg);

    form.hidden = true;
    var res = $("result"); res.hidden = false; res.focus({ preventScroll: true }); res.scrollIntoView();
  }

  // ---------- Mini formulario del hero ----------
  var quickForm = $("quickform");
  if (quickForm) {
    quickForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var n = clean($("q-nombre").value, 80);
      window.open(waLink(n ? T.waQuick(n) : T.waGeneral), "_blank", "noopener");
    });
  }

  // ---------- Calculadora de pago mensual (estimado educativo) ----------
  var calcForm = $("calcform");
  if (calcForm) {
    calcForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var res = $("calcresult");
      res.textContent = "";
      function num(id) {
        var v = parseFloat(String($(id).value).replace(/[$,\s]/g, "").replace(",", "."));
        return isNaN(v) ? 0 : v;
      }
      var price = num("c-precio"), down = num("c-inicial"), apr = num("c-apr");
      var nper = parseInt($("c-plazo").value, 10) || 60;
      var principal = price - down;
      if (price <= 0 || down < 0 || principal <= 0 || apr < 0 || apr > 60 || nper <= 0) {
        res.textContent = T.calcErr;
        return;
      }
      var r = apr / 100 / 12, m;
      if (r === 0) m = principal / nper;
      else { var f = Math.pow(1 + r, nper); m = principal * r * f / (f - 1); }
      var pretty = m.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      res.appendChild(document.createTextNode(T.calcResult(pretty)));
      res.appendChild(el("small", null, T.calcNote));
    });
  }

  // ---------- Trade-in: vende o da de enganche ----------
  var tradeForm = $("tradeform");
  if (tradeForm) {
    tradeForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = clean($("t-vehiculo").value, 80);
      window.open(waLink(T.waTrade(v)), "_blank", "noopener");
    });
  }

  // Parámetro ?vehiculo= (lista blanca; cualquier otro valor se ignora)
  try {
    var pre = resolveVehicle(new URLSearchParams(location.search).get("vehiculo"));
    if (pre) { selectVehicle(pre.slug); window.setTimeout(function () { $("plan").scrollIntoView(); }, 50); }
  } catch (e) { /* valor inválido: se ignora */ }
  showStep(0);
})();
