// City Cars Houston TX — inventario de vehículos (GENERADO por tools/build-inventory.py).
// Para cambiar el inventario: edita inventario-nuevo/inventario.csv y vuelve a correr el script.
// Variable global VEHICLES; se carga antes de i18n.js y app.js.
// REGLA: nunca precios, inicial, mensualidad, APR ni plazos en este archivo.
"use strict";
(function () {
  var COLORS = {"gris": ["Gris", "Gray"], "negro": ["Negro", "Black"], "plata": ["Plata", "Silver"], "rojo": ["Rojo", "Red"], "azul": ["Azul", "Blue"], "vinotinto": ["Vinotinto", "Burgundy"], "celeste": ["Celeste", "Light blue"], "blanco": ["Blanco", "White"], "marron": ["Marrón", "Brown"], "dorado": ["Dorado", "Gold"], "morado": ["Morado", "Purple"], "verde": ["Verde", "Green"], "beige": ["Beige", "Beige"], "naranja": ["Naranja", "Orange"], "amarillo": ["Amarillo", "Yellow"]};
  var FEAT = {"sunroof": {"es": "Quemacocos", "en": "Sunroof"}, "pano": {"es": "Techo panorámico", "en": "Panoramic roof"}, "lifted": {"es": "Elevada (lifted)", "en": "Lifted"}, "diesel": {"es": "Motor diésel", "en": "Diesel engine"}};
  var IDEAL = {"truck": {"es": "Para quien necesita una troca para trabajo y para el día a día.", "en": "For anyone who needs a truck for work and everyday driving."}, "suv": {"es": "Para familias y para quien necesita espacio para pasajeros y maletas.", "en": "For families and anyone who needs room for passengers and luggage."}, "sedan": {"es": "Para manejar todos los días en la ciudad.", "en": "For everyday driving around town."}};
  // [id, slug, carpeta, año, marca, modelo, tipo, color, millas, nº fotos, 3 filas, tracción, extras, portada]
  var RAW = [
  ];
  window.VEHICLES = RAW.map(function (r, rank) {
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
})();
