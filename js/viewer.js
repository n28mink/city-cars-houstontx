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
})();
