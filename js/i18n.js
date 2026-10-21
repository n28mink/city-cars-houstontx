// City Cars Houston TX — textos ES/EN de la interfaz.
// Variable global I18N = { es: {...}, en: {...} }; se carga antes de app.js.
"use strict";

  // ---------- Textos dinámicos ----------
  var I18N = {
    es: {
      types: { suv: "SUV", truck: "Troca", sedan: "Sedán" }, used: "Usado",
      miles: "millas",
      drive: "Tracción", driveTbd: "por confirmar", seen: "Se ve en las fotos", ideal: "Ideal para",
      dealerGeneric: "La ofrece un dealer con licencia en Houston.", dealerNamed: "La ofrece: ",
      ask: "Preguntar por WhatsApp", save: "Guardar ",
      lowMiles: "Pocas millas", usedLc: "usado", rows3Tag: "3 filas", lookingFor: "Busco: ",
      altFront: " — vista delantera",
      anyMake: "Todas las marcas", anyModel: "Todos los modelos", pickMake: "Elige una marca primero", anyYear: "Cualquiera",
      anyColor: "Todos los colores", anyMiles: "Cualquiera", milesUpTo: function (n) { return "Hasta " + n + " millas"; },
      sorts: [["best", "Mejores primero"], ["newest", "Año: más nuevos"], ["oldest", "Año: más viejos"], ["miles", "Menos millas primero"], ["az", "Marca y modelo (A–Z)"]],
      panel: "Más filtros", panelN: function (n) { return "Más filtros (" + n + ")"; }, removeFilter: "Quitar filtro: ", applyN: function (n) { return "Ver " + n + (n === 1 ? " vehículo" : " vehículos"); }, fromLbl: function (y) { return "Desde " + y; }, toLbl: function (y) { return "Hasta " + y; },
      filters: [["todos", "Todos"], ["truck", "Trocas"], ["suv", "SUV"], ["sedan", "Sedanes"], ["rows3", "3 filas"], ["4x4", "4x4 confirmada"]],
      soon: "Estamos actualizando el inventario con fotos nuevas. Escríbenos por WhatsApp al (281) 602-7044 y te mostramos lo que hay disponible.",
      empty: "No hay vehículos con esos filtros por ahora. Prueba con menos filtros o escríbenos por WhatsApp.",
      count: function (a, b) { return "Mostrando " + a + " de " + b + " vehículos"; },
      more: function (n, rest) { return "Ver " + n + " más (" + rest + " restantes)"; },
      featured: function (n, brands, total) { return "Una selección de " + n + " vehículos de " + brands + " marcas. Tenemos " + total + " en total."; },
      seeAll: function (total) { return "Ver todo el inventario (" + total + ")"; },
      favOne: "Guardaste 1: ", favMany: function (n) { return "Guardaste " + n + " vehículos"; },
      waGeneral: "Hola City Cars Houston TX, vi su página y quiero que me conecten con un dealer.",
      waCar: function (v) { return "Hola City Cars Houston TX, me interesa este vehículo: " + v + ". ¿Está disponible?"; },
      waFavs: function (list) { return "Hola City Cars Houston TX, me interesan estos vehículos: " + list + ". ¿Siguen disponibles?"; },
      cases: [
        { id: "familia", label: "Somos familia grande", text: "SUV de 3 filas como Tahoe, Suburban o Yukon, con espacio para toda la familia y las sillas de los niños.", action: "Ver 3 filas", filter: "rows3" },
        { id: "primer", label: "Es mi primer crédito", text: "Muchos de nuestros dealers trabajan con compradores sin crédito o con su primer crédito. Te decimos con quién conviene hablar.", action: "Escríbenos por WhatsApp", wa: "Hola City Cars Houston TX, es mi primer crédito (o no tengo historial crediticio). ¿Con qué dealers me pueden conectar?" },
        { id: "trabajo", label: "La necesito para trabajar", text: "Trocas de cabina doble con enganche de remolque, listas para la obra.", action: "Ver trocas", filter: "truck" },
        { id: "itin", label: "Tengo ITIN o matrícula", text: "Muchos de nuestros dealers trabajan con ITIN, matrícula consular o pasaporte. La aprobación la decide el dealer o el financiador.", action: "Escríbenos por WhatsApp", wa: "Hola City Cars Houston TX, tengo ITIN (o matrícula consular o pasaporte). ¿Con qué dealers me pueden conectar?" },
        { id: "danado", label: "Mi crédito está dañado", text: "Crédito dañado, repo o bancarrota: algunos dealers trabajan con esas situaciones. Cuéntanos y te decimos con honestidad qué esperar.", action: "Escríbenos por WhatsApp", wa: "Hola City Cars Houston TX, mi crédito está dañado (tuve un repo o una bancarrota). ¿Con qué dealers me pueden conectar?" },
        { id: "efectivo", label: "Me pagan en efectivo", text: "Si te pagan en efectivo o trabajas por tu cuenta, hay formas de comprobar ingresos. Te orientamos por WhatsApp.", action: "Escríbenos por WhatsApp", wa: "Hola City Cars Houston TX, me pagan en efectivo (o trabajo por mi cuenta). ¿Con qué dealers me pueden conectar?" }
      ],
      waTrade: function (v) { return "Hola City Cars Houston TX, tengo " + (v ? "un(a) " + v : "un vehículo") + " que quiero vender o dar de enganche. ¿Me pueden orientar?"; }
    },
    en: {
      types: { suv: "SUV", truck: "Truck", sedan: "Sedan" }, used: "Used",
      miles: "miles",
      drive: "Drive", driveTbd: "to be confirmed", seen: "Visible in the photos", ideal: "Great for",
      dealerGeneric: "Offered by a licensed Houston dealer.", dealerNamed: "Offered by: ",
      ask: "Ask on WhatsApp", save: "Save ",
      lowMiles: "Low miles", usedLc: "used", rows3Tag: "3 rows", lookingFor: "Looking for: ",
      altFront: " — front view",
      anyMake: "All makes", anyModel: "All models", pickMake: "Pick a make first", anyYear: "Any",
      anyColor: "All colors", anyMiles: "Any", milesUpTo: function (n) { return "Up to " + n + " miles"; },
      sorts: [["best", "Best first"], ["newest", "Year: newest first"], ["oldest", "Year: oldest first"], ["miles", "Lowest mileage first"], ["az", "Make & model (A–Z)"]],
      panel: "More filters", panelN: function (n) { return "More filters (" + n + ")"; }, removeFilter: "Remove filter: ", applyN: function (n) { return "Show " + n + (n === 1 ? " vehicle" : " vehicles"); }, fromLbl: function (y) { return "From " + y; }, toLbl: function (y) { return "Up to " + y; },
      filters: [["todos", "All"], ["truck", "Trucks"], ["suv", "SUVs"], ["sedan", "Sedans"], ["rows3", "3 rows"], ["4x4", "Confirmed 4x4"]],
      soon: "We are updating the inventory with new photos. Message us on WhatsApp at (281) 602-7044 and we will show you what is available.",
      empty: "Nothing matches those filters right now. Try fewer filters or message us on WhatsApp.",
      count: function (a, b) { return "Showing " + a + " of " + b + " vehicles"; },
      more: function (n, rest) { return "Show " + n + " more (" + rest + " left)"; },
      featured: function (n, brands, total) { return "A selection of " + n + " vehicles from " + brands + " brands. We have " + total + " in total."; },
      seeAll: function (total) { return "See the full inventory (" + total + ")"; },
      favOne: "You saved 1: ", favMany: function (n) { return "You saved " + n + " vehicles"; },
      waGeneral: "Hi City Cars Houston TX, I saw your website and I'd like to be matched with a dealer.",
      waCar: function (v) { return "Hi City Cars Houston TX, I'm interested in this vehicle: " + v + ". Is it still available?"; },
      waFavs: function (list) { return "Hi City Cars Houston TX, I'm interested in these vehicles: " + list + ". Are they still available?"; },
      cases: [
        { id: "familia", label: "Big family", text: "Three-row SUVs like the Tahoe, Suburban and Yukon, with room for the whole family and the car seats.", action: "See 3-row SUVs", filter: "rows3" },
        { id: "primer", label: "First car or no credit", text: "Many of our dealers work with first-time buyers and people with no credit history. We'll tell you who's worth talking to.", action: "Message us on WhatsApp", wa: "Hi City Cars Houston TX, this is my first car (or I have no credit history). Which dealers can you connect me with?" },
        { id: "trabajo", label: "I need it for work", text: "Crew cab trucks with tow hitches, ready for the job site.", action: "See trucks", filter: "truck" },
        { id: "itin", label: "I have an ITIN", text: "Many of our dealers work with ITIN, consular ID or passport. Approval is up to the dealer or lender.", action: "Message us on WhatsApp", wa: "Hi City Cars Houston TX, I have an ITIN (or consular ID or passport). Which dealers can you connect me with?" },
        { id: "danado", label: "Bad credit, repo or bankruptcy", text: "Some dealers work with bad credit, past repos or bankruptcy. Tell us your story and we'll be straight with you about what to expect.", action: "Message us on WhatsApp", wa: "Hi City Cars Houston TX, I have bad credit (a past repo or bankruptcy). Which dealers can you connect me with?" },
        { id: "efectivo", label: "Paid in cash / self-employed", text: "If you're paid in cash or work for yourself, there are ways to show income. We'll walk you through it on WhatsApp.", action: "Message us on WhatsApp", wa: "Hi City Cars Houston TX, I'm paid in cash (or self-employed). Which dealers can you connect me with?" }
      ],
      waTrade: function (v) { return "Hi City Cars Houston TX, I have " + (v ? "a " + v : "a vehicle") + " I'd like to sell or trade in. Can you point me in the right direction?"; }
    }
  };
