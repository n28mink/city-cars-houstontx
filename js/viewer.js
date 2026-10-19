// Visor de fotos de las páginas individuales de cada vehículo.
// Lee las fotos de <script type="application/json" id="photos-data"> (sin JS inline: CSP script-src 'self').
(function () {
  "use strict";
  var dataEl = document.getElementById("photos-data");
  var img = document.getElementById("vimg");
  var cnt = document.getElementById("vcount");
  if (!dataEl || !img) return;
  var PH;
  try { PH = JSON.parse(dataEl.textContent); } catch (e) { return; }
  if (!Array.isArray(PH) || !PH.length) return;

  var vi = 0;
  var strip = document.getElementById("vthumbs");

  function show(i) {
    vi = (i + PH.length) % PH.length;
    img.src = PH[vi].src;
    img.srcset = PH[vi].srcset || PH[vi].src;
    img.alt = PH[vi].alt || "";
    if (cnt) cnt.textContent = (vi + 1) + "/" + PH.length;
    if (strip) {
      Array.prototype.forEach.call(strip.children, function (b, k) {
        b.setAttribute("aria-current", String(k === vi));
      });
    }
  }

  if (strip && PH.length > 1) {
    PH.forEach(function (p, k) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "vthumb";
      b.setAttribute("aria-label", (p.alt || "Foto") + " (" + (k + 1) + "/" + PH.length + ")");
      var t = document.createElement("img");
      t.src = p.src;
      t.alt = "";
      t.loading = "lazy";
      t.decoding = "async";
      b.appendChild(t);
      b.addEventListener("click", function () { show(k); });
      strip.appendChild(b);
    });
  }

  // "Volver al inventario": si vienes de la lista, regresa a ella con tus filtros y tu posición
  var back = document.querySelector("a.back");
  if (back) back.addEventListener("click", function (e) {
    try {
      var ref = new URL(document.referrer);
      if (ref.origin === window.location.origin && /^\/(es|en)\/(index\.html)?$/.test(ref.pathname) && window.history.length > 1) {
        e.preventDefault();
        window.history.back();
      }
    } catch (err) { /* sin referrer: el enlace normal lleva al inventario */ }
  });

  var pv = document.querySelector(".viewer .prev");
  var nx = document.querySelector(".viewer .next");
  if (pv) pv.addEventListener("click", function () { show(vi - 1); });
  if (nx) nx.addEventListener("click", function () { show(vi + 1); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") show(vi + 1);
    if (e.key === "ArrowLeft") show(vi - 1);
  });
  show(0);

  // ---------- Visor ampliado (una foto a la vez): pellizcar, arrastrar, doble toque, rueda, flechas ----------
  var ES = document.documentElement.lang !== "en";
  var TX = ES
    ? { open: "Ver foto ampliada", close: "Cerrar", prev: "Foto anterior", next: "Foto siguiente", zin: "Acercar", zout: "Alejar", hint: "Pellizca o toca dos veces para acercar", dlg: "Foto ampliada" }
    : { open: "View photo full screen", close: "Close", prev: "Previous photo", next: "Next photo", zin: "Zoom in", zout: "Zoom out", hint: "Pinch or double-tap to zoom", dlg: "Enlarged photo" };
  var viewer = document.querySelector(".viewer");
  var lb = null, lbImg, stage, countEl, prevB, nextB, zinB, zoutB, hintEl, opener = null;
  var sc = 1, tx = 0, ty = 0, MAXZ = 5;
  var ptrs = {}, g = null, lastTap = 0, swipeDx = 0;

  function fitSize() {  // tamaño de la foto "completa" dentro del recuadro, sin zoom
    var w = stage.clientWidth, h = stage.clientHeight, iw = lbImg.naturalWidth || w, ih = lbImg.naturalHeight || h;
    var f = Math.min(w / iw, h / ih);
    return { w: iw * f, h: ih * f, sw: w, sh: h };
  }
  function clampPan() {
    var f = fitSize(), mx = Math.max(0, (f.w * sc - f.sw) / 2), my = Math.max(0, (f.h * sc - f.sh) / 2);
    tx = Math.min(mx, Math.max(-mx, tx)); ty = Math.min(my, Math.max(-my, ty));
  }
  function paint() {
    clampPan();
    lbImg.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + sc + ")";
    stage.classList.toggle("zoomed", sc > 1);
    zoutB.disabled = sc <= 1; zinB.disabled = sc >= MAXZ;
  }
  function setScale(ns, cx, cy) {  // zoom manteniendo fijo el punto (cx, cy) respecto al centro del recuadro
    ns = Math.min(MAXZ, Math.max(1, ns));
    var k = ns / sc; tx = cx - (cx - tx) * k; ty = cy - (cy - ty) * k; sc = ns;
    if (sc === 1) { tx = 0; ty = 0; }
    paint();
  }
  function lbShow(i) {
    var idx = (i + PH.length) % PH.length; vi = idx;
    sc = 1; tx = 0; ty = 0;
    lbImg.src = PH[idx].src; lbImg.alt = PH[idx].alt || "";
    countEl.textContent = (idx + 1) + "/" + PH.length;
    prevB.hidden = nextB.hidden = PH.length < 2;
    paint();
    show(idx);  // la foto principal de la ficha sigue a la del visor
  }
  function closeLb() {
    if (!lb) return;
    document.removeEventListener("keydown", onKey, true);
    lb.remove(); lb = null; document.body.classList.remove("lb-open");
    if (opener) opener.focus();
  }
  function onKey(e) {
    if (["Escape", "ArrowRight", "ArrowLeft", "+", "=", "-"].indexOf(e.key) > -1) e.stopPropagation();  // que no mueva también la foto de fondo
    if (e.key === "Escape") { e.preventDefault(); closeLb(); }
    else if (e.key === "ArrowRight") { e.preventDefault(); lbShow(vi + 1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); lbShow(vi - 1); }
    else if (e.key === "+" || e.key === "=") { e.preventDefault(); setScale(sc * 1.4, 0, 0); }
    else if (e.key === "-") { e.preventDefault(); setScale(sc / 1.4, 0, 0); }
    else if (e.key === "Tab") {  // el foco no sale del visor
      var f = Array.prototype.filter.call(lb.querySelectorAll("button:not([disabled])"), function (x) { return !x.hidden && x.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  }
  function btn(cls, label, text) {
    var b = document.createElement("button"); b.type = "button"; b.className = "lb-btn " + cls;
    b.setAttribute("aria-label", label); b.textContent = text; return b;
  }
  function dist(a, b) { return Math.sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y)); }
  function pts() { return Object.keys(ptrs).map(function (k) { return ptrs[k]; }); }
  function center() { var r = stage.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }

  function onDown(e) {
    if (e.target.closest && e.target.closest(".lb-btn")) return;
    try { stage.setPointerCapture(e.pointerId); } catch (err) { /* puntero sintético: sin captura */ }
    ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
    var p = pts();
    if (p.length === 2) g = { d: dist(p[0], p[1]), sc: sc, mx: (p[0].x + p[1].x) / 2, my: (p[0].y + p[1].y) / 2, tx: tx, ty: ty };
    else if (p.length === 1) { g = { x: e.clientX, y: e.clientY, tx: tx, ty: ty, moved: false }; swipeDx = 0; }
    hintEl.style.opacity = "0";
  }
  function onMove(e) {
    if (!ptrs[e.pointerId]) return;
    ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
    var p = pts(), c = center();
    if (p.length >= 2 && g && g.d) {
      var d = dist(p[0], p[1]), mx = (p[0].x + p[1].x) / 2, my = (p[0].y + p[1].y) / 2;
      var ns = Math.min(MAXZ, Math.max(1, g.sc * d / g.d)), k = ns / g.sc;
      // el punto entre los dedos queda bajo los dedos (zoom + arrastre a la vez)
      tx = (mx - c.x) - ((g.mx - c.x) - g.tx) * k; ty = (my - c.y) - ((g.my - c.y) - g.ty) * k; sc = ns;
      if (sc === 1) { tx = 0; ty = 0; }
      paint();
    } else if (p.length === 1 && g && g.x != null) {
      var dx = e.clientX - g.x, dy = e.clientY - g.y;
      if (Math.abs(dx) + Math.abs(dy) > 6) g.moved = true;
      if (sc > 1) { tx = g.tx + dx; ty = g.ty + dy; paint(); }
      else swipeDx = dx;
    }
  }
  function onUp(e) {
    if (!ptrs[e.pointerId]) return;
    delete ptrs[e.pointerId];
    var left = pts().length;
    if (left === 1) { var r = pts()[0]; g = { x: r.x, y: r.y, tx: tx, ty: ty, moved: true }; return; }
    if (left > 0) return;
    if (g && g.x != null) {
      if (sc === 1 && Math.abs(swipeDx) > 60 && PH.length > 1) lbShow(vi + (swipeDx < 0 ? 1 : -1));
      else if (!g.moved) {  // doble toque / doble clic: acerca o vuelve a la foto completa
        var now = Date.now();
        if (now - lastTap < 320) { var c = center(); sc > 1 ? setScale(1, 0, 0) : setScale(2.5, e.clientX - c.x, e.clientY - c.y); lastTap = 0; }
        else lastTap = now;
      }
    }
    g = null; swipeDx = 0;
  }
  function onWheel(e) {
    e.preventDefault();
    var c = center(); setScale(sc * (e.deltaY < 0 ? 1.2 : 1 / 1.2), e.clientX - c.x, e.clientY - c.y);
  }

  function openLb(e) {
    if (lb) return;
    opener = (e && e.currentTarget === img && zb) ? zb : document.activeElement;
    lb = document.createElement("div"); lb.className = "lb"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true"); lb.setAttribute("aria-label", TX.dlg);
    stage = document.createElement("div"); stage.className = "lb-stage";
    lbImg = document.createElement("img"); lbImg.className = "lb-img"; lbImg.draggable = false; lbImg.alt = "";
    hintEl = document.createElement("p"); hintEl.className = "lb-hint"; hintEl.textContent = TX.hint;
    prevB = btn("lb-nav lb-prev", TX.prev, "‹"); nextB = btn("lb-nav lb-next", TX.next, "›");
    stage.appendChild(lbImg); stage.appendChild(prevB); stage.appendChild(nextB); stage.appendChild(hintEl);
    var bar = document.createElement("div"); bar.className = "lb-bar";
    countEl = document.createElement("span"); countEl.className = "lb-count"; countEl.setAttribute("aria-live", "polite");
    var ctrls = document.createElement("div"); ctrls.className = "lb-ctrls";
    zoutB = btn("", TX.zout, "−"); zinB = btn("", TX.zin, "+");
    var closeB = btn("", TX.close, "×");
    ctrls.appendChild(zoutB); ctrls.appendChild(zinB); ctrls.appendChild(closeB);
    bar.appendChild(countEl); bar.appendChild(ctrls);
    lb.appendChild(stage); lb.appendChild(bar);
    document.body.appendChild(lb); document.body.classList.add("lb-open");
    prevB.addEventListener("click", function () { lbShow(vi - 1); });
    nextB.addEventListener("click", function () { lbShow(vi + 1); });
    zinB.addEventListener("click", function () { setScale(sc * 1.5, 0, 0); });
    zoutB.addEventListener("click", function () { setScale(sc / 1.5, 0, 0); });
    closeB.addEventListener("click", closeLb);
    stage.addEventListener("pointerdown", onDown);
    stage.addEventListener("pointermove", onMove);
    stage.addEventListener("pointerup", onUp);
    stage.addEventListener("pointercancel", onUp);
    stage.addEventListener("wheel", onWheel, { passive: false });
    lbImg.addEventListener("load", paint);
    window.addEventListener("resize", paint);
    document.addEventListener("keydown", onKey, true);
    lbShow(vi);
    closeB.focus();
    window.setTimeout(function () { if (hintEl) hintEl.style.opacity = "0"; }, 3500);
  }
  var zb = null;
  if (viewer) {
    zb = document.createElement("button"); zb.type = "button"; zb.className = "vzoom"; zb.setAttribute("aria-label", TX.open);
    zb.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4H4v5M15 4h5v5M9 20H4v-5M15 20h5v-5" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    viewer.appendChild(zb);
    zb.addEventListener("click", openLb);
    img.addEventListener("click", openLb);
  }
})();
