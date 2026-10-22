// City Cars Houston TX — manda la raíz "/" al idioma del navegador (es/ o en/).
// En archivo externo porque la CSP del sitio no permite <script> inline.
"use strict";
try {
  var l = String(navigator.language || "es").toLowerCase();
  location.replace(l.indexOf("en") === 0 ? "en/" : "es/");
} catch (e) {
  location.replace("es/");
}
