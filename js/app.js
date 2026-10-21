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
  var WA_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/></svg>';
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
  function titleOf(v) { return (v.yearNum ? v.yearNum + " " : "") + fullName(v); }
  function label(v) { return titleOf(v) + " " + v.color[LANG].toLowerCase() + " (" + v.id + ")"; }
  function lowMiles(v) { return v.milesNum != null && v.milesNum < 5000; }
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

  if ($("grid")) initHome();

  // ---------- Portada: casos, inventario, efectos, formularios del hero ----------
  function initHome() {
    var grid = $("grid");
    document.body.classList.add("has-bar");
    // Enlaces viejos: /es/?vehiculo=… y /es/#plan ahora van a la ficha del vehículo o al inventario
    try {
      var old = resolveVehicle(new URLSearchParams(location.search).get("vehiculo"));
      if (old) { location.replace((LANG === "en" ? "car/" : "carro/") + old.slug + "/"); return; }
      if (location.hash === "#plan") { location.replace("#inventario"); return; }
    } catch (e) { /* se ignora */ }

    // La barra fija de abajo (celular) aparece cuando el hero sale de pantalla
    var heroEl = document.querySelector(".hero");
    if (heroEl && "IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { document.body.classList.toggle("hero-in-view", en[0].intersectionRatio > 0.45); }, { threshold: [0, 0.45, 1] }).observe(heroEl);
    }

    // ---------- Casos ----------
    var caseChips = $("case-chips"), casePanel = $("case-panel"), openCase = "";
    function showCase(c) {
      openCase = c ? c.id : "";
      caseChips.querySelectorAll(".chip").forEach(function (b) { b.setAttribute("aria-pressed", String(!!c && b.dataset.id === c.id)); });
      casePanel.hidden = !c;
      casePanel.textContent = "";
      if (!c) return;
      casePanel.appendChild(el("p", null, c.text));
      var btn;
      if (c.filter) {
        btn = el("button", { type: "button", "class": "btn btn-primary" }, c.action);
        btn.addEventListener("click", function () { setFilter(c.filter); $("inventario").scrollIntoView(); });
      } else {
        btn = el("a", { "class": "btn btn-wa", target: "_blank", rel: "noopener noreferrer" });
        btn.insertAdjacentHTML("beforeend", WA_ICON);
        btn.appendChild(document.createTextNode(c.action));
        btn.href = waLink(c.wa);
      }
      casePanel.appendChild(btn);
    }
    T.cases.forEach(function (c) {
      var b = el("button", { type: "button", "class": "chip", "aria-pressed": "false", "data-id": c.id }, c.label);
      b.addEventListener("click", function () { showCase(openCase === c.id ? null : c); });
      caseChips.appendChild(b);
    });

    // ---------- Inventario ----------
    var favs = (store("cch:favs") || []).filter(function (s) { return resolveVehicle(s); });
    var filtersEl = $("filters");
    var PAGE = 24, shown = PAGE;
    var FEATURED_N = 12;   // la portada muestra una selección corta con varias marcas; el inventario completo queda en «Ver todo»
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

    // Selección de la portada: la mejor unidad de cada marca (ronda 1), luego la segunda mejor de cada una (ronda 2), etc., hasta FEATURED_N.
    // Así se ven varias marcas en vez de las 2–3 que dominan «Mejores primero» (GMC y Chevrolet son más de la mitad del inventario).
    var FEATURED = (function () {
      var byMake = {}, out = [];
      VEHICLES.slice().sort(SORTS.best).forEach(function (v) { (byMake[v.make] = byMake[v.make] || []).push(v); });
      for (var round = 0; out.length < FEATURED_N; round++) {
        var layer = Object.keys(byMake).map(function (m) { return byMake[m][round]; }).filter(Boolean).sort(SORTS.best);
        if (!layer.length) break;
        out = out.concat(layer.slice(0, FEATURED_N - out.length));
      }
      return out;
    })();
    var FEATURED_AT = {};
    FEATURED.forEach(function (v) { FEATURED_AT[v.slug] = true; });
    var FEATURED_BRANDS = uniq(FEATURED.map(function (v) { return v.make; })).length;

    // Estado de los filtros (también vive en la URL para poder volver desde una ficha o compartir la búsqueda).
    // all = «Ver todo el inventario» (ver=todo): sin filtros, la portada muestra solo la selección hasta que se pide todo.
    var F = { chip: "todos", q: "", make: "", model: "", from: "", to: "", color: "", miles: "", sort: "best", all: false };
    var PARAM = { chip: "tipo", q: "q", make: "marca", model: "modelo", from: "desde", to: "hasta", color: "color", miles: "millas", sort: "orden", all: "ver" };
    var qWords = [];
    var ctl = { from: $("f-desde"), to: $("f-hasta"), sort: $("f-orden"), q: $("q-inv") };
    var groups = { make: $("o-marca"), model: $("o-modelo"), color: $("o-color"), miles: $("o-millas") };
    var modelGroup = $("g-modelo"), chipsEl = $("fchips"), activeEl = $("factive");
    var sideEl = $("fside"), scrimEl = $("fscrim"), openBtn = $("f-open"), openN = $("f-open-n"), closeBtn = $("f-close"), applyBtn = $("f-apply");
    var clearBtns = [$("f-clear"), $("f-clear2")];

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
      if (skip !== "miles" && F.miles && !(v.milesNum != null && v.milesNum <= +F.miles)) return false;  // sin millas confirmadas no entra en este filtro
      return true;
    }
    function countBy(skip, keyOf) {
      var c = {};
      VEHICLES.forEach(function (v) { if (matches(v, skip)) { var k = keyOf(v); c[k] = (c[k] || 0) + 1; } });
      return c;
    }
    function countMiles() {
      var c = {};
      VEHICLES.forEach(function (v) {
        if (!matches(v, "miles") || v.milesNum == null) return;
        MILES_STEPS.forEach(function (m) { if (v.milesNum <= m) c[m] = (c[m] || 0) + 1; });
      });
      return c;
    }

    // Opciones como botones (una sola elección; tocar la elegida la quita). Se arman una vez y solo se actualizan los conteos.
    function buildOpts(key, container, items) {
      container.textContent = "";
      items.forEach(function (it) {
        var b = el("button", { type: "button", "class": "fopt", "data-v": it.value, "aria-pressed": "false" });
        b.appendChild(el("span", { "class": "fopt-l" }, it.label));
        b.appendChild(el("span", { "class": "fopt-n" }));
        b.addEventListener("click", function () {
          F[key] = F[key] === it.value ? "" : it.value;
          if (key === "make") F.model = "";
          refresh();
          closeDrops();
        });
        container.appendChild(b);
      });
    }
    function syncOpts(key, container, counts) {
      Array.prototype.forEach.call(container.children, function (b) {
        var v = b.getAttribute("data-v"), n = counts[v] || 0, on = F[key] === v;
        b.setAttribute("aria-pressed", String(on));
        b.querySelector(".fopt-n").textContent = String(n);
        b.disabled = n === 0 && !on;
      });
    }
    function fillYears(sel, anyLabel, values) {
      sel.textContent = "";
      sel.appendChild(el("option", { value: "" }, anyLabel));
      values.forEach(function (x) { sel.appendChild(el("option", { value: x }, x)); });
    }
    var modelBuiltFor = null;
    function syncPanel() {
      syncOpts("make", groups.make, countBy("make", function (v) { return v.make; }));
      if (modelBuiltFor !== F.make) {
        modelBuiltFor = F.make;
        var fams = F.make ? uniq(VEHICLES.filter(function (v) { return v.make === F.make; }).map(function (v) { return v.family; })).sort(byText) : [];
        buildOpts("model", groups.model, fams.map(function (f) { return { value: f, label: famLabel(F.make, f) }; }));
      }
      modelGroup.classList.toggle("no-make", !F.make);  // en celular se oculta hasta elegir marca; en escritorio el menú queda desactivado
      if (F.make) syncOpts("model", groups.model, countBy("model", function (v) { return v.family; }));
      syncOpts("color", groups.color, countBy("color", function (v) { return v.colorKey; }));
      syncOpts("miles", groups.miles, countMiles());
    }
    function activeCount() {
      return ["q", "make", "model", "from", "to", "color", "miles"].filter(function (k) { return F[k]; }).length + (F.chip !== "todos" ? 1 : 0);
    }
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
      var n = activeCount();
      openN.textContent = n ? "(" + n + ")" : "";
      filtersEl.querySelectorAll(".chip").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.id === F.chip)); });
      ctl.from.value = F.from; ctl.to.value = F.to; ctl.sort.value = F.sort;
      syncDrops();
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
          var val = k === "all" ? (F.all ? "todo" : "") : F[k];
          if (val && val !== def) u.searchParams.set(PARAM[k], val); else u.searchParams.delete(PARAM[k]);
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
      F.all = get("all") === "todo";
    }
    function refresh() {
      shown = PAGE;
      qWords = norm(F.q).split(/\s+/).filter(Boolean);
      syncPanel(); syncChrome(); saveState(); renderGrid();
    }

    // Listas fijas: marca, color, millas, años y orden
    buildOpts("make", groups.make, MAKES.map(function (m) { return { value: m, label: m }; }));
    buildOpts("color", groups.color, COLOR_KEYS.map(function (k) { return { value: k, label: colorNames[k] }; }));
    buildOpts("miles", groups.miles, MILES_STEPS.map(function (m) { return { value: String(m), label: T.milesUpTo(thousands(m)) }; }));
    fillYears(ctl.from, T.anyYear, YEARS.map(String));
    fillYears(ctl.to, T.anyYear, YEARS.map(String));
    ctl.sort.textContent = "";
    T.sorts.forEach(function (s) { ctl.sort.appendChild(el("option", { value: s[0] }, s[1])); });

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
    ctl.sort.addEventListener("change", function () { F.sort = ctl.sort.value; refresh(); });
    ctl.q.addEventListener("input", function () { F.q = clean(ctl.q.value, 60); refresh(); });
    clearBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        F.chip = "todos"; F.q = ""; F.make = ""; F.model = ""; F.from = ""; F.to = ""; F.color = ""; F.miles = "";
        refresh();
        if (!sheetOpen()) ctl.q.focus({ preventScroll: true });
      });
    });

    // Escritorio: cada grupo de filtros es un menú desplegable de la barra superior (en celular los grupos siguen siendo secciones de la hoja)
    var CHEVRON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var drops = [["make", "g-marca", "o-marca"], ["model", "g-modelo", "o-modelo"], ["year", "g-anio", "o-anio"], ["color", "g-color", "o-color"], ["miles", "g-millas", "o-millas"]].map(function (d) {
      var g = $(d[1]), legend = g.querySelector("legend, .flegend");
      var btn = el("button", { type: "button", "class": "fdrop", "aria-expanded": "false", "aria-controls": d[2] });
      btn.appendChild(el("span"));
      btn.insertAdjacentHTML("beforeend", CHEVRON);  // solo el SVG fijo de este archivo
      g.insertBefore(btn, $(d[2]));
      var o = { key: d[0], g: g, btn: btn, name: legend.textContent };
      btn.addEventListener("click", function () {
        var open = !g.classList.contains("open");
        closeDrops(o);
        g.classList.toggle("open", open); btn.setAttribute("aria-expanded", String(open));
      });
      return o;
    });
    function closeDrops(except) {
      drops.forEach(function (d) {
        if (d === except || !d.g.classList.contains("open")) return;
        d.g.classList.remove("open"); d.btn.setAttribute("aria-expanded", "false");
      });
    }
    function dropValue(key) {
      if (key === "make") return F.make;
      if (key === "model") return F.model ? famLabel(F.make, F.model) : "";
      if (key === "year") return F.from && F.to ? F.from + " – " + F.to : F.from ? T.fromLbl(F.from) : F.to ? T.toLbl(F.to) : "";
      if (key === "color") return F.color ? colorNames[F.color] : "";
      return F.miles ? T.milesUpTo(thousands(F.miles)) : "";
    }
    function syncDrops() {
      drops.forEach(function (d) {
        var v = dropValue(d.key);
        d.btn.firstChild.textContent = v ? d.name + ": " + v : d.name;
        d.btn.classList.toggle("on", !!v);
        if (d.key === "model") { d.btn.disabled = !F.make; d.btn.title = F.make ? "" : T.pickMake; }
      });
    }
    document.addEventListener("click", function (e) { if (!(e.target.closest && e.target.closest(".fgroup"))) closeDrops(); });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      drops.forEach(function (d) { if (d.g.classList.contains("open")) { closeDrops(); d.btn.focus(); } });
    });
    document.addEventListener("keyup", function (e) {  // al salir con Tab de un menú abierto, se cierra
      if (e.key !== "Tab") return;
      drops.forEach(function (d) { if (d.g.classList.contains("open") && !d.g.contains(document.activeElement)) closeDrops(); });
    });

    // Celular: los filtros se abren como una hoja desde abajo.
    function sheetOpen() { return sideEl.classList.contains("open"); }
    function openSheet() {
      sideEl.classList.add("open"); scrimEl.hidden = false;
      sideEl.setAttribute("role", "dialog"); sideEl.setAttribute("aria-modal", "true");
      document.body.classList.add("sheet-open"); openBtn.setAttribute("aria-expanded", "true");
      closeBtn.focus();
    }
    function closeSheet() {
      if (!sheetOpen()) return;
      sideEl.classList.remove("open"); scrimEl.hidden = true;
      sideEl.removeAttribute("role"); sideEl.removeAttribute("aria-modal");
      document.body.classList.remove("sheet-open"); openBtn.setAttribute("aria-expanded", "false");
      openBtn.focus();
    }
    openBtn.addEventListener("click", openSheet);
    closeBtn.addEventListener("click", closeSheet);
    applyBtn.addEventListener("click", function () {
      if (featuredOn() && !F.all) { F.all = true; refresh(); }   // «Ver N vehículos» sin filtros: el inventario completo, no solo la selección
      closeSheet(); var g = $("grid"); if (g) g.scrollIntoView();
    });
    scrimEl.addEventListener("click", closeSheet);
    document.addEventListener("keydown", function (e) {
      if (!sheetOpen()) return;
      if (e.key === "Escape") { closeSheet(); return; }
      if (e.key !== "Tab") return;
      var f = Array.prototype.filter.call(sideEl.querySelectorAll("button:not([disabled]),select"), function (x) { return x.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    if (window.matchMedia) {
      var wide = window.matchMedia("(min-width: 901px)");
      var onWide = function () { if (wide.matches && sheetOpen()) closeSheet(); };
      if (wide.addEventListener) wide.addEventListener("change", onWide); else if (wide.addListener) wide.addListener(onWide);
    }

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
    // La foto llena el marco 4:3 (cover): todas las tarjetas se ven iguales, sin franjas ni difuminado.
    function photoLink(v, sheetUrl, idx) {
      var ph = photoSrc(v.photos[v.cover - 1] || v.photos[0], "640");
      var a = el("a", { "class": "ph", href: sheetUrl, tabindex: "-1", "aria-hidden": "true" });  // el título es el enlace accesible
      var img = el("img", {
        src: ph.src, srcset: ph.srcset, sizes: "(max-width: 700px) 100vw, 400px",
        width: "640", height: "480", loading: idx < 3 ? "eager" : "lazy", decoding: "async",
        alt: titleOf(v) + " " + v.color[LANG].toLowerCase() + T.altFront
      });
      a.appendChild(img);
      return a;
    }
    function favButton(v) {
      var fav = icon(el("button", { type: "button", "class": "fav", "aria-pressed": String(favs.indexOf(v.slug) > -1), "aria-label": T.save + titleOf(v) }), HEART);
      fav.addEventListener("click", function () { toggleFav(v.slug, fav); });
      return fav;
    }

    var moreBtn = $("more"), countEl = $("inv-count");
    if (!VEHICLES.length) {  // inventario en actualización: sin filtros ni tarjetas, solo el aviso
      document.querySelectorAll("#inventario .fbar, #fside, #inventario .inv-top, #filters, #factive").forEach(function (n) { n.hidden = true; });
      if (countEl) countEl.hidden = true;
    }
    // Sin filtros ni orden elegido, la selección con varias marcas va primero y el resto sigue en «Mejores primero».
    function featuredOn() { return VEHICLES.length > FEATURED_N && F.sort === "best" && activeCount() === 0; }
    function visibleList() {
      var list = VEHICLES.filter(function (v) { return matches(v); }).sort(SORTS[F.sort]);
      if (featuredOn()) list = FEATURED.concat(list.filter(function (v) { return !FEATURED_AT[v.slug]; }));
      return list;
    }
    function renderGrid(focusSlug) {
      grid.textContent = "";
      var list = visibleList();
      var curated = featuredOn() && !F.all;      // portada: solo la selección, hasta que se pida «Ver todo el inventario»
      var limit = curated ? FEATURED_N : shown;
      var hash = decodeURIComponent((window.location.hash || "").slice(1));  // enlace directo a una tarjeta lejana
      if (hash) {
        for (var hi = 0; hi < list.length; hi++) {
          if (list[hi].slug !== hash || hi < limit) continue;
          if (curated) { F.all = true; curated = false; saveState(); limit = shown; }
          if (hi >= limit) { shown = Math.ceil((hi + 1) / PAGE) * PAGE; limit = shown; }
          break;
        }
      }
      if (countEl) countEl.textContent = curated && FEATURED_BRANDS > 1 ? T.featured(Math.min(limit, list.length), FEATURED_BRANDS, list.length) : T.count(Math.min(limit, list.length), list.length);
      applyBtn.textContent = T.applyN(list.length);
      if (!list.length) { if (moreBtn) moreBtn.hidden = true; grid.appendChild(el("p", { "class": "lead" }, VEHICLES.length ? T.empty : T.soon)); return; }
      list.slice(0, limit).forEach(function (v, i) {
        var card = el("article", { "class": "car", id: v.slug, "aria-label": titleOf(v) });
        var sheetUrl = (LANG === "en" ? "car/" : "carro/") + v.slug + "/";
        card.appendChild(photoLink(v, sheetUrl, i));
        if (lowMiles(v)) card.appendChild(el("span", { "class": "tag" }, T.lowMiles));
        card.appendChild(favButton(v));

        var body = el("div", { "class": "car-body" });
        var head = el("div", { "class": "car-head" });
        var h3 = el("h3");
        h3.appendChild(el("a", { href: sheetUrl }, titleOf(v)));
        head.appendChild(h3);
        head.appendChild(el("span", { "class": "car-id" }, v.id));
        body.appendChild(head);
        body.appendChild(el("p", { "class": "car-meta" }, v.color[LANG] + ", " + T.usedLc));

        var facts = el("ul", { "class": "facts" });   // solo lo que se sabe: nada de "por confirmar" en la tarjeta
        [v.milesNum != null ? milesText(v, LANG) : "", T.types[v.type], v.drive === "4x4" ? "4x4" : "", v.rows3 ? T.rows3Tag : ""].forEach(function (t) {
          if (t) facts.appendChild(el("li", null, t));
        });
        body.appendChild(facts);

        var ask = el("a", { "class": "btn btn-wa", target: "_blank", rel: "noopener noreferrer", "aria-label": T.ask + ": " + titleOf(v) });
        ask.insertAdjacentHTML("beforeend", WA_ICON);   // SVG fijo de este archivo
        ask.appendChild(document.createTextNode(T.ask));
        ask.href = waLink(T.waCar(label(v)));
        body.appendChild(ask);
        card.appendChild(body);
        grid.appendChild(card);
      });
      if (moreBtn) {
        if (curated) { moreBtn.hidden = false; moreBtn.className = "btn btn-primary btn-lg"; moreBtn.textContent = T.seeAll(list.length); }
        else { moreBtn.hidden = limit >= list.length; moreBtn.className = "btn btn-ghost"; moreBtn.textContent = T.more(Math.min(PAGE, list.length - limit), list.length - limit); }
      }
      if (focusSlug) { var fc = document.getElementById(focusSlug); var fl = fc && fc.querySelector("h3 a"); if (fl) fl.focus(); }
    }
    if (moreBtn) moreBtn.addEventListener("click", function () {
      if (featuredOn() && !F.all) {  // de la selección al inventario completo: las mismas tarjetas siguen arriba y se suman las siguientes
        F.all = true; shown = PAGE; saveState();
        var next = visibleList()[FEATURED_N];
        renderGrid(next && next.slug);
        return;
      }
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
    refresh();
    renderFavbar();

    // ---------- Trade-in: vende o da de enganche ----------
    var tradeForm = $("tradeform");
    if (tradeForm) {
      tradeForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var v = clean($("t-vehiculo").value, 80);
        window.open(waLink(T.waTrade(v)), "_blank", "noopener");
      });
    }
  }

})();
