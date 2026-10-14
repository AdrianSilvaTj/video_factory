"""Research-backed starter ideas. Claims remain tied to source records."""

IDEAS = {
    "pulpo-anillos-azules": {
        "topic": "Pulpo de anillos azules",
        "aliases": ["pulpo de anillos azules", "pulpo anillos azules", "blue-ringed octopus"],
        "niche": "animales y naturaleza",
        "locale": "es-CO",
        "hook": "Parece llevar luces de neón, pero ese azul es una advertencia.",
        "sources": [{
            "source_id": "src-australian-museum-blue-lined-octopus",
            "title": "Blue-lined Octopus (Hapalochlaena fasciata)",
            "publisher": "Australian Museum",
            "author": "Australian Museum",
            "url": "https://australian.museum/learn/animals/molluscs/blue-lined-octopus/",
            "retrieved_at": "2026-10-06",
            "license_or_terms": "Se usa como referencia factual; no se reutilizan sus imágenes.",
            "notes": "Describe marcas azules de advertencia, conducta tímida, tetrodotoxina en el veneno y riesgo de parálisis respiratoria. La página trata específicamente Hapalochlaena fasciata.",
        }],
        "claims": [
            {"claim_id": "c1", "text": "El blue-lined octopus muestra marcas azules cuando es perturbado.", "source_ids": ["src-australian-museum-blue-lined-octopus"], "status": "verified", "scope_note": "La fuente se refiere a Hapalochlaena fasciata; no generalizar cada detalle a todas las especies."},
            {"claim_id": "c2", "text": "Su veneno paralizante se conoce como tetrodotoxina.", "source_ids": ["src-australian-museum-blue-lined-octopus"], "status": "verified"},
            {"claim_id": "c3", "text": "La exposición puede afectar los músculos respiratorios.", "source_ids": ["src-australian-museum-blue-lined-octopus"], "status": "verified"},
            {"claim_id": "c4", "text": "La especie descrita suele ser tímida y puede morder si se la manipula.", "source_ids": ["src-australian-museum-blue-lined-octopus"], "status": "verified"},
            {"claim_id": "c5", "text": "El blue-lined octopus descrito mide alrededor de 4,5 cm.", "source_ids": ["src-australian-museum-blue-lined-octopus"], "status": "verified", "scope_note": "Tamaño de la especie Hapalochlaena fasciata, no de todas las especies de pulpo de anillos azules."},
        ],
        "script": [
            {"scene_id": "s1", "claim_ids": [], "narration": "Parece llevar luces de neón, pero ese azul es una advertencia.", "caption": "Ese azul es una advertencia"},
            {"scene_id": "s2", "claim_ids": ["c1"], "narration": "En una especie de pulpo de anillos azules, las marcas brillantes aparecen cuando se siente perturbada.", "caption": "Las marcas aparecen al sentirse amenazado"},
            {"scene_id": "s3", "claim_ids": ["c2"], "narration": "Su veneno contiene tetrodotoxina, una neurotoxina paralizante.", "caption": "Tetrodotoxina: neurotoxina paralizante"},
            {"scene_id": "s4", "claim_ids": ["c3"], "narration": "Una mordedura puede afectar la respiración, aunque casi no se note al principio.", "caption": "Puede comprometer la respiración"},
            {"scene_id": "s5", "claim_ids": ["c4"], "narration": "Es tímido, pero manipularlo puede ser peligroso. Si lo ves, admíralo de lejos.", "caption": "Admíralo de lejos; no lo manipules"},
            {"scene_id": "s6", "claim_ids": ["c5"], "narration": "¿Esperabas una defensa tan potente en un animal que mide apenas unos centímetros?", "caption": "¿Lo sabías? Cuéntame abajo"},
        ],
        "cta": "¿Lo sabías? Cuéntame abajo.",
    },
    "camaron-mantis": {
        "topic": "Camarón mantis",
        "aliases": ["camarón mantis", "camaron mantis", "mantis shrimp"],
        "niche": "animales y naturaleza",
        "locale": "es-CO",
        "hook": "Este cazador marino puede golpear tan rápido que el agua también golpea.",
        "sources": [
            {"source_id": "src-patek-2004", "title": "Biomechanics: deadly strike mechanism of a mantis shrimp", "publisher": "Nature / PubMed", "author": "Patek, Korff y Caldwell", "url": "https://pubmed.ncbi.nlm.nih.gov/15103366/", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; no se reutilizan las figuras.", "notes": "Estudio de alta velocidad sobre apéndices raptores, burbujas de cavitación y el mecanismo del golpe de Odontodactylus scyllarus."},
            {"source_id": "src-smithsonian-mantis-cavitation", "title": "Behold the Mantis Shrimp", "publisher": "Smithsonian Institution", "author": "Smithsonian", "url": "https://www.si.edu/collections/snapshot/behold-mantis-shrimp", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; no se reutilizan imágenes.", "notes": "Describe el golpe, la cavitación y los tipos de apéndices usados para romper o arponear presas."},
            {"source_id": "src-smithsonian-polarized-vision", "title": "Built-in Underwater Polarized Lenses?", "publisher": "Smithsonian Ocean", "author": "Smithsonian Ocean", "url": "https://ocean.si.edu/ocean-life/invertebrates/built-underwater-polarized-lenses", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; no se reutilizan imágenes.", "notes": "Explica la detección de luz polarizada y su posible papel en la comunicación."}
        ],
        "claims": [
            {"claim_id": "c1", "text": "Los camarones mantis tienen apéndices raptores que usan para golpear conchas o arponear presas.", "source_ids": ["src-patek-2004", "src-smithsonian-mantis-cavitation"], "status": "verified"},
            {"claim_id": "c2", "text": "En Odontodactylus scyllarus, el golpe veloz forma burbujas de vapor alrededor de la presa.", "source_ids": ["src-patek-2004"], "status": "verified", "scope_note": "El mecanismo fue estudiado en esta especie; no generalizar todas las cifras a todos los estomatópodos."},
            {"claim_id": "c3", "text": "La formación y el colapso de las burbujas de cavitación pueden añadir fuerzas destructivas al impacto.", "source_ids": ["src-patek-2004"], "status": "verified"},
            {"claim_id": "c4", "text": "El camarón mantis puede detectar luz polarizada; se investiga su uso para comunicarse.", "source_ids": ["src-smithsonian-polarized-vision"], "status": "verified", "scope_note": "El papel comunicativo se describe como posible, no definitivo."}
        ],
        "script": [
            {"scene_id": "s1", "claim_ids": ["c1"], "narration": "Este cazador marino puede golpear tan rápido que el agua también golpea.", "caption": "El agua también golpea"},
            {"scene_id": "s2", "claim_ids": ["c1"], "narration": "El camarón mantis usa apéndices como mazas para romper conchas o atrapar presas.", "caption": "Mazas o arpones naturales"},
            {"scene_id": "s3", "claim_ids": ["c2"], "narration": "En una especie, el golpe veloz crea burbujas de vapor junto a la presa.", "caption": "Un golpe que crea burbujas"},
            {"scene_id": "s4", "claim_ids": ["c3"], "narration": "Al colapsar, esas burbujas añaden fuerzas al impacto: no es un golpe cualquiera.", "caption": "La cavitación suma fuerza"},
            {"scene_id": "s5", "claim_ids": ["c4"], "narration": "Y además detecta luz polarizada, una señal que podría ayudarle a comunicarse bajo el agua.", "caption": "También ve luz polarizada"},
            {"scene_id": "s6", "claim_ids": [], "narration": "¿Cuál de sus habilidades te sorprendió más? Te leo en los comentarios.", "caption": "¿Cuál te sorprendió más?"}
        ],
        "visual_assets": [
            {"asset_id": "asset-mantis-01", "filename": "mantis-01-apertura.png", "description": "Camarón mantis pavo real en un arrecife, plano de apertura."},
            {"asset_id": "asset-mantis-02", "filename": "mantis-02-apendices.png", "description": "Apéndices raptores del camarón mantis."},
            {"asset_id": "asset-mantis-03", "filename": "mantis-03-golpe.png", "description": "Golpe contra una concha y burbujas de cavitación."},
            {"asset_id": "asset-mantis-04", "filename": "mantis-04-ojos.png", "description": "Detalle de los ojos compuestos."},
            {"asset_id": "asset-mantis-05", "filename": "mantis-05-arrecife.png", "description": "Camarón mantis saliendo de su madriguera."}
        ],
        "cta": "¿Cuál de sus habilidades te sorprendió más? Te leo en los comentarios."
    },
    "tardigrado": {
        "topic": "Tardígrado",
        "aliases": ["tardígrado", "tardigrado", "tardigrades", "oso de agua"],
        "niche": "animales y naturaleza",
        "locale": "es-CO",
        "hook": "Este animal microscópico puede secarse casi por completo y esperar a que vuelva el agua.",
        "sources": [
            {"source_id": "src-nsf-tardigrade-dehydration", "title": "How do microscopic creatures called tardigrades survive being completely dried out?", "publisher": "U.S. National Science Foundation", "author": "NSF", "url": "https://www.nsf.gov/news/how-do-microscopic-creatures-called-tardigrades", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; no se reutiliza la imagen.", "notes": "Resume resultados de investigación sobre tamaño, desecación y mecanismos protectores."},
            {"source_id": "src-plos-tardigrade-anhydrobiosis", "title": "How long can tardigrades survive in the anhydrobiotic state?", "publisher": "PLOS ONE", "author": "Bertolani et al.", "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0270386", "retrieved_at": "2026-10-06", "license_or_terms": "Artículo científico de acceso abierto; revisar licencia para reutilizar material gráfico.", "notes": "Compara varias especies y condiciones; informa diferencias de supervivencia y retorno a la actividad, además de exposición experimental al vacío espacial."},
            {"source_id": "src-nasa-cs04", "title": "Cell Science-04: Using Water Bears to Identify Biological Countermeasures to Stress During Multigenerational Spaceflight", "publisher": "NASA", "author": "NASA", "url": "https://science.nasa.gov/biological-physical/investigations/cell-science-04/", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; no se reutiliza contenido audiovisual.", "notes": "Describe el estudio de tardígrados en la Estación Espacial Internacional."}
        ],
        "claims": [
            {"claim_id": "c1", "text": "Los tardígrados miden menos de medio milímetro.", "source_ids": ["src-nsf-tardigrade-dehydration"], "status": "verified", "scope_note": "Tamaño típico aproximado; hay variación entre especies."},
            {"claim_id": "c2", "text": "Algunas especies se contraen y pierden casi toda su agua en anhidrobiosis, formando un tun.", "source_ids": ["src-nsf-tardigrade-dehydration", "src-plos-tardigrade-anhydrobiosis"], "status": "verified", "scope_note": "Capacidad y respuesta dependen de especie y condiciones."},
            {"claim_id": "c3", "text": "En anhidrobiosis, la actividad metabólica cae de forma extrema.", "source_ids": ["src-plos-tardigrade-anhydrobiosis"], "status": "verified"},
            {"claim_id": "c4", "text": "Ensayos con tardígrados deshidratados encontraron supervivencia tras exposiciones experimentales al vacío espacial.", "source_ids": ["src-plos-tardigrade-anhydrobiosis"], "status": "verified", "scope_note": "Resultado condicionado por las especies y protocolos estudiados; no implica invulnerabilidad."},
            {"claim_id": "c5", "text": "La capacidad de volver a la actividad tras la anhidrobiosis varía entre especies y se relaciona con las condiciones y duración del estado.", "source_ids": ["src-plos-tardigrade-anhydrobiosis"], "status": "verified"}
        ],
        "script": [
            {"scene_id": "s1", "claim_ids": ["c1"], "narration": "Se llama oso de agua y es tan pequeño que necesitas un microscopio.", "caption": "El oso de agua"},
            {"scene_id": "s2", "claim_ids": ["c2"], "narration": "Cuando su hábitat se seca, algunas especies pierden casi toda su agua.", "caption": "Puede perder casi toda el agua"},
            {"scene_id": "s3", "claim_ids": ["c2", "c3"], "narration": "Su cuerpo se contrae y su actividad cae casi por completo.", "caption": "Entra en modo tun"},
            {"scene_id": "s4", "claim_ids": ["c4"], "narration": "En pruebas controladas, algunos ejemplares secos sobrevivieron al vacío espacial.", "caption": "Algunos sobrevivieron al vacío"},
            {"scene_id": "s5", "claim_ids": ["c5"], "narration": "No es inmortal: la resistencia cambia entre especies y condiciones.", "caption": "Resistentes, pero no invencibles"},
            {"scene_id": "s6", "claim_ids": ["c5"], "narration": "Con agua de nuevo, algunos vuelven a moverse. ¿Ya lo sabías?", "caption": "¿Ya conocías al oso de agua?"}
        ],
        "visual_assets": [
            {"asset_id": "asset-tardigrade-01", "filename": "tardigrado-01-musgo.png", "description": "Tardígrado activo sobre musgo."},
            {"asset_id": "asset-tardigrade-02", "filename": "tardigrado-02-tun.png", "description": "Tardígrado contraído en estado tun mientras el musgo se seca."},
            {"asset_id": "asset-tardigrade-03", "filename": "tardigrado-03-microscopio.png", "description": "Tardígrado observado bajo microscopio."},
            {"asset_id": "asset-tardigrade-04", "filename": "tardigrado-04-vacio.png", "description": "Ilustración conceptual del tardígrado en estado tun en un entorno espacial."},
            {"asset_id": "asset-tardigrade-05", "filename": "tardigrado-05-agua.png", "description": "Tardígrado retomando actividad junto a una gota de agua."}
        ],
        "cta": "¿Ya conocías al oso de agua? Cuéntame y comparte este dato."
    },
    "salar-de-uyuni": {
        "topic": "Salar de Uyuni",
        "aliases": ["salar de uyuni", "salar uyuni", "uyuni"],
        "niche": "lugares asombrosos",
        "locale": "es-CO",
        "hook": "En Bolivia existe un espejo tan grande que parece no tener fin.",
        "sources": [
            {"source_id": "src-nasa-uyuni-topography", "title": "Topography of the Flattest Surface on Earth: using ICESAT, GPS, and MISR to Measure Salt Surface Topography on Salar de Uyuni, Bolivia", "publisher": "NASA Technical Reports Server", "author": "Comstock y Bills", "url": "https://ntrs.nasa.gov/citations/20050071074", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; el resumen indica public use permitted.", "notes": "Describe el tamaño, la planicie, las inundaciones estacionales y el mapeo de agua en el salar."},
            {"source_id": "src-nasa-uyuni-rainy-season", "title": "A Salt Bath in Bolivia", "publisher": "NASA Earth Observatory", "author": "NASA", "url": "https://earthobservatory.nasa.gov/images/149502/a-salt-bath-in-bolivia", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; no se reutilizan imágenes.", "notes": "Describe su enorme extensión y la apariencia de espejo causada por agua durante la temporada lluviosa."},
            {"source_id": "src-usgs-uyuni-minerals", "title": "Introduction to the geology of the Salar de Uyuni", "publisher": "U.S. Geological Survey", "author": "USGS", "url": "https://pubs.usgs.gov/of/1995/0618/report.pdf", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; no se reutilizan figuras.", "notes": "Describe la costra de sal, salmuera y recursos minerales, incluido litio."}
        ],
        "claims": [
            {"claim_id": "c1", "text": "El Salar de Uyuni, en el Altiplano boliviano, es el salar más grande del mundo y mide cerca de 9.800 km².", "source_ids": ["src-nasa-uyuni-topography"], "status": "verified"},
            {"claim_id": "c2", "text": "Salvo algunas islas de roca, su superficie presenta menos de 40 cm de relieve en el área descrita por el estudio.", "source_ids": ["src-nasa-uyuni-topography"], "status": "verified", "scope_note": "Medición del resumen del estudio NASA citado, no una afirmación de perfección matemática."},
            {"claim_id": "c3", "text": "En época lluviosa, agua poco profunda puede cubrir parte del salar y crear un efecto de espejo.", "source_ids": ["src-nasa-uyuni-topography", "src-nasa-uyuni-rainy-season"], "status": "verified"},
            {"claim_id": "c4", "text": "La costra de sal cubre salmuera que contiene litio y otros minerales.", "source_ids": ["src-usgs-uyuni-minerals"], "status": "verified"}
        ],
        "script": [
            {"scene_id": "s1", "claim_ids": ["c1"], "narration": "En Bolivia existe un espejo tan grande que parece no tener fin.", "caption": "Un espejo sin fin"},
            {"scene_id": "s2", "claim_ids": ["c1"], "narration": "Es el Salar de Uyuni, el salar más grande del mundo, con casi diez mil kilómetros cuadrados.", "caption": "Casi diez mil kilómetros cuadrados"},
            {"scene_id": "s3", "claim_ids": ["c2"], "narration": "Salvo algunas islas rocosas, su superficie varía menos de cuarenta centímetros de altura.", "caption": "Una superficie casi plana"},
            {"scene_id": "s4", "claim_ids": ["c3"], "narration": "En temporada de lluvias, una capa de agua cubre parte de la sal y refleja el cielo.", "caption": "El cielo se refleja en la sal"},
            {"scene_id": "s5", "claim_ids": ["c4"], "narration": "Bajo la costra hay salmuera con litio y otros minerales.", "caption": "Salmuera rica en minerales"},
            {"scene_id": "s6", "claim_ids": [], "narration": "¿Lo visitarías en época seca o cuando se convierte en espejo?", "caption": "¿Seco o como espejo?"}
        ],
        "visual_assets": [
            {"asset_id": "asset-uyuni-01", "filename": "uyuni-01-apertura.png", "description": "Vista panorámica del Salar de Uyuni bajo un cielo inmenso."},
            {"asset_id": "asset-uyuni-02", "filename": "uyuni-02-crustas.png", "description": "Patrones geométricos en la costra de sal seca."},
            {"asset_id": "asset-uyuni-03", "filename": "uyuni-03-isla.png", "description": "Isla rocosa con cactus rodeada por el salar."},
            {"asset_id": "asset-uyuni-04", "filename": "uyuni-04-espejo.png", "description": "Capa de agua poco profunda que refleja el cielo."},
            {"asset_id": "asset-uyuni-05", "filename": "uyuni-05-atardecer.png", "description": "Horizonte del salar al atardecer con luz reflejada."}
        ],
        "cta": "¿Lo visitarías en época seca o cuando se convierte en espejo?"
    },
    "rio-hirviente-amazonico": {
        "topic": "Río hirviente de la Amazonía",
        "aliases": ["rio hirviente amazonico", "río hirviente", "boiling river"],
        "niche": "lugares asombrosos",
        "locale": "es-CO",
        "hook": "En plena selva peruana, hay tramos de un río que superan los 95 grados.",
        "sources": [
            {"source_id": "src-gcb-boiling-river-2024", "title": "Thermal Gradients Along a Geothermal River Shape Tropical Forest Communities", "publisher": "Global Change Biology", "author": "Fortier et al.", "url": "https://doi.org/10.1111/gcb.17555", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia factual; el artículo describe un estudio de investigación.", "notes": "Mide el gradiente térmico del río hirviente en la Amazonía peruana; aguas supercalientes entran por fallas, superan 95 °C y se enfrían aguas abajo."},
            {"source_id": "src-aapg-agua-caliente", "title": "The Agua Caliente Oilfield and the Boiling River of the Peruvian Amazon", "publisher": "AAPG Explorer", "author": "Andrés Ruzo", "url": "https://www.aapg.org/articles/the-agua-caliente-oilfield-and-the-boiling-river-of-the-peruvian-amazon/", "retrieved_at": "2026-10-06", "license_or_terms": "Referencia contextual; no se reutiliza contenido gráfico.", "notes": "Contexto geológico e histórico sobre surgencias termales y la cuenca del río."}
        ],
        "claims": [
            {"claim_id": "c1", "text": "En el río hirviente de la Amazonía central peruana, el agua supera los 95 °C en los tramos de entrada de aguas geotermales.", "source_ids": ["src-gcb-boiling-river-2024"], "status": "verified", "scope_note": "La temperatura extrema corresponde a tramos específicos, no a todo el curso."},
            {"claim_id": "c2", "text": "Aguas supercalientes ascienden por fallas y entran al cauce.", "source_ids": ["src-gcb-boiling-river-2024"], "status": "verified"},
            {"claim_id": "c3", "text": "El agua se enfría gradualmente río abajo antes de unirse al Pachitea.", "source_ids": ["src-gcb-boiling-river-2024"], "status": "verified"},
            {"claim_id": "c4", "text": "El calor del río eleva la temperatura del bosque ribereño, que funciona como gradiente natural para estudiar efectos térmicos en plantas tropicales.", "source_ids": ["src-gcb-boiling-river-2024"], "status": "verified"}
        ],
        "script": [
            {"scene_id": "s1", "claim_ids": ["c1"], "narration": "En plena Amazonía peruana, hay tramos de río que superan los noventa y cinco grados Celsius.", "caption": "Más de 95 grados Celsius"},
            {"scene_id": "s2", "claim_ids": ["c1", "c2"], "narration": "No todo el río hierve: aguas supercalientes entran por fallas y calientan partes del cauce.", "caption": "No todo el río está hirviendo"},
            {"scene_id": "s3", "claim_ids": ["c3"], "narration": "A medida que avanza, el agua se enfría antes de llegar al río Pachitea.", "caption": "Se enfría río abajo"},
            {"scene_id": "s4", "claim_ids": ["c4"], "narration": "Ese calor también cambia la temperatura del bosque que crece junto al río.", "caption": "Un bosque calentado por el río"},
            {"scene_id": "s5", "claim_ids": ["c4"], "narration": "Por eso, científicos estudian allí cómo responde la vegetación tropical al calor.", "caption": "Un laboratorio natural"},
            {"scene_id": "s6", "claim_ids": [], "narration": "Su temperatura puede causar quemaduras graves: admíralo siempre desde un lugar seguro.", "caption": "Obsérvalo desde un lugar seguro"}
        ],
        "visual_assets": [
            {"asset_id": "asset-boiling-01", "filename": "rio-01-apertura.png", "description": "Vista aérea del río caliente entre la selva amazónica."},
            {"asset_id": "asset-boiling-02", "filename": "rio-02-vapor.png", "description": "Vapor elevándose sobre un tramo caliente del río."},
            {"asset_id": "asset-boiling-03", "filename": "rio-03-falla.png", "description": "Ilustración geológica conceptual de agua calentada que emerge por fallas."},
            {"asset_id": "asset-boiling-04", "filename": "rio-04-bosque.png", "description": "Bosque tropical ribereño calentado por el gradiente térmico."},
            {"asset_id": "asset-boiling-05", "filename": "rio-05-observacion.png", "description": "Investigadores observan el río desde un punto seguro."}
        ],
        "cta": "Su temperatura puede causar quemaduras graves: admíralo siempre desde un lugar seguro."
    }
    ,"gran-agujero-azul": {
        "topic": "Gran Agujero Azul de Belice",
        "aliases": ["gran agujero azul", "blue hole belice", "great blue hole"],
        "niche": "lugares asombrosos", "locale": "es-CO",
        "hook": "Desde el aire parece un ojo oscuro abierto en medio del Caribe.",
        "sources": [
            {"source_id":"src-unesco-belize-reef","title":"Belize Barrier Reef Reserve System","publisher":"UNESCO World Heritage Centre","author":"UNESCO","url":"https://whc.unesco.org/en/list/764/","retrieved_at":"2026-10-06","license_or_terms":"Referencia factual; no se reutilizan imágenes.","notes":"Incluye el Blue Hole Natural Monument y describe el paisaje submarino y geológico del arrecife."},
            {"source_id":"src-belize-blue-hole","title":"The Blue Hole Natural Monument","publisher":"Belize Tourism Board","author":"Belize Tourism Board","url":"https://belizetourismboard.org/wp-content/uploads/2022/08/BTB_WEB_TRAVELGUIDE-ENGLISH1.pdf","retrieved_at":"2026-10-06","license_or_terms":"Referencia factual; no se reutilizan imágenes.","notes":"Describe el sumidero submarino dentro del Lighthouse Reef Atoll y las estalactitas de la antigua cueva colapsada."}
        ],
        "claims": [
            {"claim_id":"c1","text":"El Gran Agujero Azul es un gran sumidero submarino situado dentro del atolón Lighthouse Reef, en Belice.","source_ids":["src-belize-blue-hole","src-unesco-belize-reef"],"status":"verified"},
            {"claim_id":"c2","text":"Sus paredes guardan estalactitas formadas cuando la cueva estaba sobre el nivel del mar.","source_ids":["src-belize-blue-hole"],"status":"verified"},
            {"claim_id":"c3","text":"El Blue Hole Natural Monument forma parte del Sistema de Reservas de la Barrera del Arrecife de Belice.","source_ids":["src-unesco-belize-reef"],"status":"verified"},
            {"claim_id":"c4","text":"El arrecife de Belice reúne distintos tipos de arrecifes, cayos, manglares y lagunas costeras.","source_ids":["src-unesco-belize-reef"],"status":"verified"}
        ],
        "script": [
            {"scene_id":"s1","claim_ids":["c1"],"narration":"Mira bien el mar del Caribe. ¿Ves ese círculo azul tan oscuro? Es una cueva inundada.","caption":"Un círculo oscuro en el Caribe"},
            {"scene_id":"s2","claim_ids":["c1"],"narration":"Se llama Gran Agujero Azul y está en el atolón Lighthouse Reef, frente a Belice.","caption":"Lighthouse Reef, Belice"},
            {"scene_id":"s3","claim_ids":["c2"],"narration":"Sus paredes conservan estalactitas: pistas de cuando este espacio estaba seco.","caption":"Una cueva que quedó bajo el mar"},
            {"scene_id":"s4","claim_ids":["c3"],"narration":"Hoy es un monumento natural dentro de la barrera de arrecife protegida de Belice.","caption":"Parte del arrecife protegido"},
            {"scene_id":"s5","claim_ids":["c4"],"narration":"A su alrededor hay arrecifes, cayos y aguas llenas de vida marina.","caption":"Un paisaje submarino diverso"},
            {"scene_id":"s6","claim_ids":[],"narration":"¿Te atreverías a mirar este abismo desde un barco o buceando?","caption":"¿Barco o buceo?"}
        ],
        "visual_assets": [
            {"asset_id":"asset-bluehole-01","filename":"bluehole-01-aereo.png","description":"Vista aérea vertical del anillo coralino y el círculo azul oscuro en el mar caribeño."},
            {"asset_id":"asset-bluehole-02","filename":"bluehole-02-borde.png","description":"Vista desde el agua del borde turquesa del atolón y el centro azul profundo."},
            {"asset_id":"asset-bluehole-03","filename":"bluehole-03-cueva.png","description":"Ilustración geológica submarina conceptual de la cueva inundada con estalactitas."},
            {"asset_id":"asset-bluehole-04","filename":"bluehole-04-arrecife.png","description":"Arrecife de coral colorido en aguas claras de Belice."},
            {"asset_id":"asset-bluehole-05","filename":"bluehole-05-buzo.png","description":"Buzo pequeño junto a una pared submarina enorme; escena contemplativa."}
        ],
        "cta":"¿Te atreverías a mirar este abismo desde un barco o buceando?"
    },
    "pamukkale": {
        "topic":"Pamukkale, el castillo de algodón", "aliases":["pamukkale","hierapolis pamukkale"], "niche":"lugares asombrosos", "locale":"es-CO",
        "hook":"En Turquía, un manantial caliente creó terrazas blancas que parecen nieve.",
        "sources":[{"source_id":"src-unesco-pamukkale","title":"Hierapolis-Pamukkale","publisher":"UNESCO World Heritage Centre","author":"UNESCO","url":"https://whc.unesco.org/en/list/485","retrieved_at":"2026-10-08","license_or_terms":"Referencia factual; no se reutilizan imágenes.","notes":"Aguas de manantiales cargadas de calcita emergen de un acantilado de casi 200 metros y forman terrazas, pozas y cascadas petrificadas. Hierápolis fue una ciudad termal helenística junto a los manantiales."}],
        "claims":[
            {"claim_id":"c1","text":"Aguas de manantiales cargadas de calcita formaron las terrazas blancas de Pamukkale.","source_ids":["src-unesco-pamukkale"],"status":"verified"},
            {"claim_id":"c2","text":"Las aguas minerales crearon cascadas petrificadas y piscinas escalonadas.","source_ids":["src-unesco-pamukkale"],"status":"verified"},
            {"claim_id":"c3","text":"Hierápolis fue una ciudad termal helenística establecida junto a los manantiales.","source_ids":["src-unesco-pamukkale"],"status":"verified"},
            {"claim_id":"c4","text":"Las fuentes de Pamukkale emergen de un acantilado de casi 200 metros.","source_ids":["src-unesco-pamukkale"],"status":"verified"}
        ],
        "script":[
            {"scene_id":"s1","claim_ids":["c1","c4"],"narration":"¡Parece nieve, pero son terrazas de roca formadas por agua caliente!","caption":"","duration_seconds":5.0},
            {"scene_id":"s2","claim_ids":["c1"],"narration":"Esto es Pamukkale, en Turquía: manantiales cargados de calcita.","caption":"Manantiales cargados de calcita"},
            {"scene_id":"s3","claim_ids":["c1","c2"],"narration":"Al brotar, el agua deja minerales que forman piscinas escalonadas y cascadas petrificadas.","caption":"El agua construye terrazas de piedra"},
            {"scene_id":"s4","claim_ids":["c2"],"narration":"Con el tiempo, los depósitos crean el travertino blanco que cubre las pozas.","caption":"Travertino blanco, creado poco a poco"},
            {"scene_id":"s5","claim_ids":["c3"],"narration":"Junto a ellas está Hierápolis, una antigua ciudad termal griega.","caption":"Hierápolis, ciudad termal antigua"},
            {"scene_id":"s6","claim_ids":["c4"],"narration":"Los manantiales brotan desde un acantilado de casi doscientos metros.","caption":"Un acantilado de casi 200 metros"}
        ],
        "source_clip_plan":[
            {"scene_id":"s1","filename":"apertura-pamukkale.png","effect":"hold"},
            {"scene_id":"s2","filename":"pamukkale-pexels-vertical.mp4","at_ratio":0.20},
            {"scene_id":"s3","filename":"pamukkale-formacion-calcita.png"},
            {"scene_id":"s4","filename":"pamukkale-pexels-aereo.mp4","at_ratio":0.35},
            {"scene_id":"s5","filename":"hierapolis-reconstruccion.png"},
            {"scene_id":"s6","filename":"pamukkale-pexels-panoramica.mp4","at_ratio":0.52},
            {"scene_id":"cta-subscribe","filename":"pamukkale-pexels-vertical.mp4","at_ratio":0.72}
        ],
        "stock_media":[
            {"filename":"pamukkale-pexels-vertical.mp4","platform":"Pexels","title":"Scenic Pamukkale Travertine Terraces in Turkey","creator":"Rose TheGuide","page_url":"https://www.pexels.com/video/scenic-pamukkale-travertine-terraces-in-turkey-30682359/","download_url":"https://videos.pexels.com/video-files/30682359/13129087_1080_1920_30fps.mp4","license":"Pexels License; free use and modification; attribution not required."},
            {"filename":"pamukkale-pexels-aereo.mp4","platform":"Pexels","title":"Stunning Aerial of Pamukkale's Travertine Pools","creator":"Rose TheGuide","page_url":"https://www.pexels.com/video/stunning-aerial-of-pamukkale-s-travertine-pools-30404182/","download_url":"https://videos.pexels.com/video-files/30404182/13030336_1080_1920_60fps.mp4","license":"Pexels License; free use and modification; attribution not required."},
            {"filename":"pamukkale-pexels-panoramica.mp4","platform":"Pexels","title":"Drone Footage of Pamukkale's Natural Geological Formations","creator":"Roman Odintsov","page_url":"https://www.pexels.com/video/drone-footage-of-natural-geological-formations-7038580/","download_url":"https://videos.pexels.com/video-files/7038580/7038580-uhd_4096_1974_30fps.mp4","license":"Pexels License; free use and modification; attribution not required."}
        ],
        "generated_media":[
            {"filename":"apertura-pamukkale.png","creator":"OpenAI image generation","license":"AI-generated artistic illustration based on UNESCO facts; not documentary footage.","prompt_summary":"3D infographic of the travertine terraces, near-200 m cliff and spring water with calcite."},
            {"filename":"pamukkale-formacion-calcita.png","creator":"OpenAI image generation","license":"AI-generated educational reconstruction; not documentary footage.","prompt_summary":"Close view of water depositing calcite and forming travertine pools."},
            {"filename":"hierapolis-reconstruccion.png","creator":"OpenAI image generation","license":"AI-generated artistic reconstruction; not documentary footage.","prompt_summary":"Ancient Hierapolis beside Pamukkale's terraces."}
        ],
        "cta":"Si te gustan los lugares asombrosos, dale like y suscríbete.",
        "social_caption":"Pamukkale parece nieve, pero sus terrazas blancas son travertino formado por agua de manantial cargada de calcita. Las fuentes emergen de un acantilado de casi 200 metros y crearon piscinas escalonadas y cascadas petrificadas.\n\n#Pamukkale #Turquia #LugaresAsombrosos #Geologia #UNESCO #Naturaleza #Reels #Shorts #TikTok"
    },    "lago-baikal": {
        "topic":"Lago Baikal y sus burbujas congeladas", "aliases":["lago baikal","baikal"], "niche":"lugares asombrosos", "locale":"es-CO",
        "hook":"Bajo el hielo transparente del Baikal parecen flotar miles de burbujas.",
        "sources":[
            {"source_id":"src-unesco-baikal","title":"Lake Baikal","publisher":"UNESCO World Heritage Centre","author":"UNESCO","url":"https://whc.unesco.org/en/list/754/","retrieved_at":"2026-10-06","license_or_terms":"Referencia factual; no se reutilizan imágenes.","notes":"Describe su edad, profundidad y reserva de agua dulce no congelada."},
            {"source_id":"src-nasa-baikal-bubbles","title":"Methane Bubbles Frozen in Lake Baikal","publisher":"NASA Science","author":"NASA","url":"https://science.nasa.gov/image-article/apod-2024-december-29-methane-bubbles-frozen-in-lake-baikal/","retrieved_at":"2026-10-06","license_or_terms":"Referencia factual; no se reutilizan imágenes.","notes":"Explica que burbujas ascendentes de metano quedan congeladas en el hielo invernal."}
        ],
        "claims":[
            {"claim_id":"c1","text":"El Baikal es el lago más profundo y uno de los más antiguos del mundo.","source_ids":["src-unesco-baikal"],"status":"verified"},
            {"claim_id":"c2","text":"Contiene cerca de una quinta parte de las reservas mundiales de agua dulce superficial no congelada.","source_ids":["src-unesco-baikal"],"status":"verified"},
            {"claim_id":"c3","text":"Burbujas de metano ascendentes quedaron congeladas en el hielo invernal del lago.","source_ids":["src-nasa-baikal-bubbles"],"status":"verified"},
            {"claim_id":"c4","text":"El lago alberga una fauna de agua dulce excepcional con especies endémicas.","source_ids":["src-unesco-baikal"],"status":"verified"}
        ],
        "script":[
            {"scene_id":"s1","claim_ids":["c3"],"narration":"Mira bajo el hielo. Esas burbujas parecen suspendidas en el tiempo.","caption":"Burbujas atrapadas en el hielo"},
            {"scene_id":"s2","claim_ids":["c3"],"narration":"En invierno, burbujas de metano que suben desde el lago pueden quedar congeladas en la superficie.","caption":"Metano congelado en el hielo"},
            {"scene_id":"s3","claim_ids":["c1"],"narration":"Este es el lago Baikal, en Siberia: el lago más profundo del planeta.","caption":"El lago más profundo del mundo"},
            {"scene_id":"s4","claim_ids":["c2"],"narration":"Y guarda cerca de una quinta parte del agua dulce superficial no congelada del mundo.","caption":"Una reserva enorme de agua dulce"},
            {"scene_id":"s5","claim_ids":["c4"],"narration":"Sus aguas también son hogar de especies que no viven en ningún otro lugar.","caption":"Vida única en sus aguas"},
            {"scene_id":"s6","claim_ids":[],"narration":"¿Habías visto burbujas atrapadas así en un lago?","caption":"¿Habías visto algo así?"}
        ],
        "visual_assets":[
            {"asset_id":"asset-baikal-01","filename":"baikal-01-hielo.png","description":"Hielo claro del lago Baikal con burbujas bajo la superficie, fotografía vertical."},
            {"asset_id":"asset-baikal-02","filename":"baikal-02-metan.png","description":"Primer plano de burbujas de metano congeladas en capas de hielo azul."},
            {"asset_id":"asset-baikal-03","filename":"baikal-03-vista.png","description":"Vasta extensión del lago Baikal congelado, horizonte siberiano invernal."},
            {"asset_id":"asset-baikal-04","filename":"baikal-04-profundidad.png","description":"Vista conceptual desde arriba del azul profundo del Baikal bajo un hielo translúcido."},
            {"asset_id":"asset-baikal-05","filename":"baikal-05-vida.png","description":"Nerpa, foca endémica del Baikal, asomando en agua abierta entre placas de hielo."}
        ],
        "cta":"¿Habías visto burbujas atrapadas así en un lago?"
    },
    "wulingyuan": {
        "topic":"Wulingyuan, los pilares de piedra de China", "aliases":["wulingyuan","zhangjiajie","pilares de piedra de china"], "niche":"lugares asombrosos", "locale":"es-CO",
        "hook":"En China hay miles de columnas de roca que atraviesan la niebla.",
        "sources":[{"source_id":"src-unesco-wulingyuan","title":"Wulingyuan Scenic and Historic Interest Area","publisher":"UNESCO World Heritage Centre","author":"UNESCO","url":"https://whc.unesco.org/en/list/640","retrieved_at":"2026-10-06","license_or_terms":"Referencia factual; no se reutilizan imágenes.","notes":"Describe más de 3.000 pilares de arenisca de cuarzo, muchos de más de 200 metros, además de gargantas, cascadas y puentes naturales."}],
        "claims":[
            {"claim_id":"c1","text":"El área de Wulingyuan en Hunan, China, está dominada por más de 3.000 pilares y picos estrechos de arenisca de cuarzo.","source_ids":["src-unesco-wulingyuan"],"status":"verified"},
            {"claim_id":"c2","text":"Muchos pilares de Wulingyuan superan los 200 metros de altura.","source_ids":["src-unesco-wulingyuan"],"status":"verified"},
            {"claim_id":"c3","text":"Entre las formaciones hay gargantas, arroyos, pozas, cascadas, cuevas y puentes naturales.","source_ids":["src-unesco-wulingyuan"],"status":"verified"},
            {"claim_id":"c4","text":"La niebla y las nubes suelen cubrir parte del paisaje de Wulingyuan.","source_ids":["src-unesco-wulingyuan"],"status":"verified"}
        ],
        "script":[
            {"scene_id":"s1","claim_ids":["c1","c4"],"narration":"Cuando baja la niebla, aparecen montañas que parecen flotar.","caption":"Montañas entre las nubes"},
            {"scene_id":"s2","claim_ids":["c1"],"narration":"Estamos en Wulingyuan, China, donde se alzan más de tres mil pilares de arenisca.","caption":"Más de 3.000 pilares de roca"},
            {"scene_id":"s3","claim_ids":["c2"],"narration":"Algunos superan los doscientos metros. Imagina verlos desde el fondo del valle.","caption":"Algunos pasan de 200 metros"},
            {"scene_id":"s4","claim_ids":["c3"],"narration":"Entre ellos hay gargantas, ríos, cascadas y cuevas escondidas.","caption":"Gargantas y cascadas entre pilares"},
            {"scene_id":"s5","claim_ids":["c4"],"narration":"La niebla cambia el paisaje a cada momento y hace que las cumbres parezcan suspendidas.","caption":"La niebla transforma el paisaje"},
            {"scene_id":"s6","claim_ids":[],"narration":"¿Te gustaría recorrer este bosque de piedra?","caption":"¿Lo recorrerías?"}
        ],
        "visual_assets":[
            {"asset_id":"asset-wulingyuan-01","filename":"wulingyuan-01-neblina.png","description":"Pilares de arenisca de Wulingyuan emergiendo de nubes matinales, vertical cinematográfico."},
            {"asset_id":"asset-wulingyuan-02","filename":"wulingyuan-02-altura.png","description":"Pilares de cuarzo y arenisca vistos desde abajo para mostrar su escala monumental."},
            {"asset_id":"asset-wulingyuan-03","filename":"wulingyuan-03-garganta.png","description":"Garganta verde con arroyo entre torres de piedra verticales."},
            {"asset_id":"asset-wulingyuan-04","filename":"wulingyuan-04-cascada.png","description":"Cascada entre formaciones rocosas altas y vegetación subtropical."},
            {"asset_id":"asset-wulingyuan-05","filename":"wulingyuan-05-panoramica.png","description":"Panorama de pilares de piedra de Wulingyuan con nubes bajas al atardecer."}
        ],
        "cta":"¿Te gustaría recorrer este bosque de piedra?"
    },
    "hipopotamo": {
        "topic":"Hipopótamo: datos curiosos", "aliases":["hipopotamo","hipopótamo","hippopotamus"], "niche":"animales y naturaleza", "locale":"es-CO",
        "hook":"Parece torpe, pero el hipopótamo guarda secretos dentro y fuera del agua.",
        "sources":[
            {"source_id":"src-adw-hippo","title":"Hippopotamus amphibius (hippopotamus)","publisher":"Animal Diversity Web, University of Michigan","author":"Animal Diversity Web","url":"https://animaldiversity.org/accounts/Hippopotamus_amphibius/","retrieved_at":"2026-10-07","license_or_terms":"Referencia factual; no se reutilizan imágenes.","notes":"Describe el pastoreo al anochecer y la permanencia diurna en el agua."},
            {"source_id":"src-nature-hippo-sweat","title":"The red sweat of the hippopotamus","publisher":"Nature","author":"Hashimoto et al.","url":"https://www.nature.com/articles/429363a","retrieved_at":"2026-10-07","license_or_terms":"Referencia factual de investigación; no se reutilizan figuras.","notes":"Describe los pigmentos rojos y anaranjados de la secreción, su absorción de luz UV y propiedades protectoras estudiadas."},
            {"source_id":"src-pretoria-hippo","title":"Hippopotamus","publisher":"National Zoological Garden of South Africa","author":"National Zoological Garden of South Africa","url":"https://www.pretoriazoo.org/animals/hippopotamus/","retrieved_at":"2026-10-07","license_or_terms":"Referencia factual; no se reutilizan imágenes.","notes":"Indica que pueden cerrar orejas y fosas nasales y que las crías pueden mamar bajo el agua."}
        ],
        "claims":[
            {"claim_id":"c1","text":"Los hipopótamos pasan buena parte del día en el agua y salen al anochecer para pastar.","source_ids":["src-adw-hippo"],"status":"verified"},
            {"claim_id":"c2","text":"Una secreción rojiza del hipopótamo no es sangre; contiene pigmentos que absorben radiación ultravioleta y pueden ayudar a proteger la piel.","source_ids":["src-nature-hippo-sweat"],"status":"verified","scope_note":"La función de protección frente a UV está respaldada; no afirmar que sea un antibiótico clínicamente probado."},
            {"claim_id":"c3","text":"Al sumergirse, el hipopótamo puede cerrar las fosas nasales y las orejas.","source_ids":["src-pretoria-hippo"],"status":"verified"},
            {"claim_id":"c4","text":"Las crías de hipopótamo pueden mamar bajo el agua.","source_ids":["src-pretoria-hippo"],"status":"verified"}
        ],
        "script":[
            {"scene_id":"s1","claim_ids":[],"narration":"Parece torpe, pero el hipopótamo guarda secretos dentro y fuera del agua.","caption":"Un gigante lleno de sorpresas"},
            {"scene_id":"s2","claim_ids":["c1"],"narration":"Durante el día pasa horas en el agua. Al anochecer sale a pastar en tierra.","caption":"De día en el agua; de noche, a pastar"},
            {"scene_id":"s3","claim_ids":["c2"],"narration":"Y ese líquido rojizo no es sangre: es una secreción con pigmentos que ayudan a proteger su piel del sol.","caption":"No es sangre: ayuda a proteger su piel"},
            {"scene_id":"s4","claim_ids":["c3"],"narration":"Cuando se sumerge, puede cerrar las fosas nasales y las orejas para que no les entre agua.","caption":"Cierra nariz y orejas bajo el agua"},
            {"scene_id":"s5","claim_ids":["c4"],"narration":"Y las crías pueden mamar bajo el agua mientras mantienen esos orificios cerrados.","caption":"Las crías también maman bajo el agua"},
            {"scene_id":"s6","claim_ids":[],"narration":"¿Cuál de estos datos te sorprendió más? Te leo en los comentarios.","caption":"¿Cuál dato te sorprendió más?"}
        ],
        "source_clip_plan":[
            {"scene_id":"s1","filename":"12611242_1080_1920_60fps.mp4","at_ratio":0.45},
            {"scene_id":"s2","filename":"20725387-hd_1080_1920_30fps.mp4","at_ratio":0.48},
            {"scene_id":"s3","filename":"15028167_2160_3840_30fps.mp4","at_ratio":0.12},
            {"scene_id":"s4","filename":"12611242_1080_1920_60fps.mp4","at_ratio":0.67},
            {"scene_id":"s5","filename":"20613007-hd_1080_1920_30fps.mp4","at_ratio":0.5},
            {"scene_id":"s6","filename":"15028167_2160_3840_30fps.mp4","at_ratio":0.68}
        ],
        "cta":"¿Cuál de estos datos te sorprendió más? Te leo en los comentarios.",
        "social_caption":"El hipopótamo parece tranquilo, pero su vida entre el agua y la tierra esconde sorpresas. Mira estos datos curiosos hasta el final.\n\n#Hipopotamo #Animales #Naturaleza #DatosCuriosos #VidaSalvaje #Reels #Shorts #TikTok"
    },
    "geiseres": {
        "topic": "Géiseres: cómo se forman",
        "aliases": ["geiser", "géiser", "geiseres", "géiseres", "geyser"],
        "niche": "ciencia y naturaleza",
        "locale": "es-CO",
        "hook": "Un géiser es una olla a presión natural escondida bajo tus pies.",
        "sources": [
            {"source_id": "src-nps-geyser-works", "title": "How Geysers Work", "publisher": "Yellowstone National Park, National Park Service", "author": "National Park Service", "url": "https://www.nps.gov/features/yell/tours/fountainpaint/geyser_works.htm", "retrieved_at": "2026-10-07", "license_or_terms": "Referencia factual; no se reutilizan imágenes.", "notes": "Explica los tres componentes y cómo los estrechamientos retienen presión hasta iniciar la erupción."},
            {"source_id": "src-nps-hydrothermal-features", "title": "Hydrothermal Features", "publisher": "Yellowstone National Park, National Park Service", "author": "National Park Service", "url": "https://www.nps.gov/yell/learn/nature/hydrothermal-features.htm", "retrieved_at": "2026-10-07", "license_or_terms": "Referencia factual; no se reutilizan imágenes.", "notes": "Distingue géiseres de aguas termales y describe el proceso de erupción."},
            {"source_id": "src-nps-hydrothermal-systems", "title": "Hydrothermal Systems", "publisher": "Yellowstone National Park, National Park Service", "author": "National Park Service", "url": "https://www.nps.gov/yell/learn/nature/hydrothermal-systems.htm", "retrieved_at": "2026-10-07", "license_or_terms": "Referencia factual; no se reutilizan imágenes.", "notes": "Describe el calor volcánico, la recarga de agua y los conductos subterráneos."}
        ],
        "claims": [
            {"claim_id": "c1", "text": "Para que exista un géiser hacen falta calor, agua y un sistema de conductos subterráneos.", "source_ids": ["src-nps-geyser-works"], "status": "verified"},
            {"claim_id": "c2", "text": "El agua de lluvia y nieve se filtra por fracturas y se calienta al acercarse a rocas calientes.", "source_ids": ["src-nps-geyser-works", "src-nps-hydrothermal-systems"], "status": "verified"},
            {"claim_id": "c3", "text": "La presión de las capas superiores puede mantener el agua caliente en estado líquido bajo tierra.", "source_ids": ["src-nps-hydrothermal-features", "src-nps-hydrothermal-systems"], "status": "verified"},
            {"claim_id": "c4", "text": "Los estrechamientos del conducto impiden que el calor escape con facilidad y ayudan a acumular presión.", "source_ids": ["src-nps-geyser-works", "src-nps-hydrothermal-features"], "status": "verified"},
            {"claim_id": "c5", "text": "Cuando la presión cae cerca de la superficie, parte del agua se convierte rápidamente en vapor y empuja la erupción.", "source_ids": ["src-nps-geyser-works", "src-nps-hydrothermal-features"], "status": "verified"}
        ],
        "script": [
            {"scene_id": "s1", "claim_ids": [], "narration": "Un géiser es una olla a presión natural escondida bajo tus pies.", "caption": "Una olla a presión natural"},
            {"scene_id": "s2", "claim_ids": ["c1"], "narration": "Para que aparezca, se necesitan tres cosas: calor, agua y una red de conductos bajo tierra.", "caption": "Calor, agua y conductos"},
            {"scene_id": "s3", "claim_ids": ["c2"], "narration": "La lluvia y la nieve se filtran por grietas y llegan a rocas calentadas por la actividad volcánica.", "caption": "El agua se calienta bajo tierra"},
            {"scene_id": "s4", "claim_ids": ["c3"], "narration": "Allá abajo, la presión puede mantener el agua líquida incluso por encima de su punto normal de ebullición.", "caption": "Agua sobrecalentada y presurizada"},
            {"scene_id": "s5", "claim_ids": ["c4"], "narration": "El conducto tiene estrechamientos que atrapan calor y presión, como la tapa de una olla.", "caption": "El conducto retiene la presión"},
            {"scene_id": "s6", "claim_ids": ["c5"], "narration": "Cuando la presión baja, el agua hierve de golpe, el vapor se expande y lanza la columna hacia el cielo.", "caption": "La presión dispara la erupción"}
        ],
        "source_clip_plan": [
            {"scene_id": "s1", "filename": "geyser-strokkur-pexels.mp4", "at_ratio": 0.35},
            {"scene_id": "s2", "filename": "geothermal-steam-pexels.mp4", "at_ratio": 0.18},
            {"scene_id": "s3", "filename": "geyser-winter-aerial-pexels.mp4", "at_ratio": 0.20},
            {"scene_id": "s4", "filename": "geothermal-steam-pexels.mp4", "at_ratio": 0.55},
            {"scene_id": "s5", "filename": "geyser-strokkur-pexels.mp4", "at_ratio": 0.72},
            {"scene_id": "s6", "filename": "geyser-winter-aerial-pexels.mp4", "at_ratio": 0.65}
        ],
        "stock_media": [
            {"filename": "geyser-strokkur-pexels.mp4", "platform": "Pexels", "title": "Captivating Eruption of Icelandic Geysir", "creator": "Edvinas Jakunskas", "page_url": "https://www.pexels.com/video/captivating-eruption-of-icelandic-geysir-31661627/", "download_url": "https://videos.pexels.com/video-files/31661627/13489518_2160_3840_30fps.mp4", "license": "Pexels License; free use and modification; attribution not required. Downloaded 2026-10-07."},
            {"filename": "geothermal-steam-pexels.mp4", "platform": "Pexels", "title": "Steaming Geothermal Geyser Eruption Outdoors", "creator": "Gylfi Gylfason", "page_url": "https://www.pexels.com/video/steaming-geothermal-geyser-eruption-outdoors-31285710/", "download_url": "https://videos.pexels.com/video-files/31285710/13359606_3840_2160_30fps.mp4", "license": "Pexels License; free use and modification; attribution not required. Downloaded 2026-10-07."},
            {"filename": "geyser-winter-aerial-pexels.mp4", "platform": "Pexels", "title": "Aerial View of Icelandic Geyser Eruption in Winter", "creator": "Sergey Guk", "page_url": "https://www.pexels.com/video/aerial-view-of-icelandic-geyser-eruption-in-winter-29415894/", "download_url": "https://videos.pexels.com/video-files/29415894/12666766_3840_2160_60fps.mp4", "license": "Pexels License; free use and modification; attribution not required. Downloaded 2026-10-07."}
        ],
        "cta": "¿Te imaginabas que un géiser funcionaba como una olla a presión?",
        "social_caption": "Calor, agua y una red subterránea convierten a los géiseres en verdaderas ollas a presión naturales.\n\n#Geiseres #Géiser #Naturaleza #Ciencia #Yellowstone #Iceland #Reels #Shorts #TikTok"
    },
    "carbonifero": {
        "topic": "Carbonífero: insectos gigantes",
        "aliases": ["carbonifero", "carbonífero", "meganeura", "insectos gigantes del carbonifero"],
        "niche": "ciencia y prehistoria",
        "locale": "es-CO",
        "hook": "¡Mira sus setenta centímetros de alas junto a una persona!",
        "sources": [
            {"source_id": "src-pnas-insect-size-history", "title": "Environmental and biotic controls on the evolutionary history of insect body size", "publisher": "Proceedings of the National Academy of Sciences", "author": "Clapham & Karr", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3390886/", "retrieved_at": "2026-10-07", "license_or_terms": "Referencia científica; no se reutilizan figuras.", "notes": "Estudia más de 10.500 longitudes de alas fósiles; las mayores envergaduras de insectos paleozoicos alcanzaban unos 70 cm y el oxígeno no explica por sí solo toda la historia del tamaño."},
            {"source_id": "src-nature-oxygen-insect-gigantism-2026", "title": "Oxygen supply through the tracheolar–muscle system does not constrain insect gigantism", "publisher": "Nature", "author": "Snelling et al.", "url": "https://www.nature.com/articles/s41586-026-10291-3", "retrieved_at": "2026-10-07", "license_or_terms": "Referencia científica; no se reutilizan figuras.", "notes": "Estudio de 2026 que cuestiona que la difusión de oxígeno en el músculo limite el tamaño máximo de insectos gigantes."},
            {"source_id": "src-smithsonian-carboniferous-air", "title": "The History of Air", "publisher": "Smithsonian Magazine", "author": "M.R. O'Connor", "url": "https://www.smithsonianmag.com/science-nature/the-history-of-air-21082166/", "retrieved_at": "2026-10-07", "license_or_terms": "Referencia contextual; no se reutilizan imágenes.", "notes": "Describe los bosques pantanosos y la hipótesis histórica que relaciona oxígeno elevado y gigantismo de artrópodos."}
        ],
        "claims": [
            {"claim_id": "c1", "text": "Meganeura fue un insecto volador extinto, parecido a una libélula, con una envergadura cercana a 70 centímetros.", "source_ids": ["src-pnas-insect-size"], "status": "verified"},
            {"claim_id": "c2", "text": "Los insectos gigantes del Carbonífero vivieron hace alrededor de 300 millones de años.", "source_ids": ["src-pnas-insect-size", "src-smithsonian-carboniferous-air"], "status": "verified"},
            {"claim_id": "c3", "text": "La atmósfera del Carbonífero tuvo niveles de oxígeno más altos que los actuales.", "source_ids": ["src-pnas-insect-size", "src-smithsonian-carboniferous-air"], "status": "verified"},
            {"claim_id": "c4", "text": "Un estudio de 2026 cuestiona que la difusión de oxígeno por sí sola limite el tamaño máximo de los insectos.", "source_ids": ["src-nature-oxygen-insect-gigantism-2026"], "status": "verified"},
            {"claim_id": "c5", "text": "La mayoría de los insectos de ese tiempo no alcanzaba tamaños gigantes; los ejemplares enormes eran excepcionales.", "source_ids": ["src-pnas-insect-size"], "status": "verified"}
        ],
        "script": [
            {"scene_id": "s1", "claim_ids": ["c1"], "narration": "¡Mira sus setenta centímetros de alas junto a una persona!", "caption": "", "duration_seconds": 5.0},
            {"scene_id": "s2", "claim_ids": ["c1", "c2"], "narration": "Hace 300 millones de años, Meganeura volaba sobre pantanos. Era una griffinfly extinta, pariente de las libélulas.", "caption": "Una griffinfly de hace 300 millones de años"},
            {"scene_id": "s3", "claim_ids": ["c1"], "narration": "Su envergadura alcanzaba unos 70 centímetros: varias veces la de una libélula actual.", "caption": "Varias veces mayor que una libélula actual"},
            {"scene_id": "s4", "claim_ids": ["c3", "c4"], "narration": "El Carbonífero tenía más oxígeno, pero su papel en el tamaño gigante aún se debate.", "caption": "El oxígeno no explica todo"},
            {"scene_id": "s5", "claim_ids": ["c5"], "narration": "Además, estos insectos enormes eran excepcionales. ¿Te atreverías a verla?", "caption": "Los gigantes eran excepcionales"},
            {"scene_id": "cta-subscribe", "claim_ids": [], "narration": "Si te gustan estos datos curiosos, dale like y suscríbete.", "caption": "Dale like y suscríbete", "purpose": "channel_subscribe_cta"}
        ],
        "source_clip_plan": [
            {"scene_id": "s1", "filename": "grafico_tamaños.png", "effect": "hold"},
            {"scene_id": "s2", "filename": "reconstruccion-carbonifero-meganeura-01.png"},
            {"scene_id": "s3", "filename": "libelula-macro-pexels.mp4", "at_ratio": 0.12},
            {"scene_id": "s4", "filename": "reconstruccion-carbonifero-meganeura-02.png"},
            {"scene_id": "s5", "filename": "libelulas-agua-pexels.mp4", "at_ratio": 0.20},
            {"scene_id": "cta-subscribe", "filename": "reconstruccion-carbonifero-meganeura-01.png"}
        ],
        "stock_media": [
            {"filename": "libelula-macro-pexels.mp4", "platform": "Pexels", "title": "A Close-Up Video of a Dragonfly", "creator": "Kelly", "page_url": "https://www.pexels.com/video/a-close-up-video-of-a-dragonfly-9480807/", "download_url": "https://videos.pexels.com/video-files/9480807/9480807-uhd_3840_2160_24fps.mp4", "license": "Pexels License; free use and modification; attribution not required. Shows a modern dragonfly, not Meganeura."},
            {"filename": "libelulas-agua-pexels.mp4", "platform": "Pexels", "title": "Dragonflies Flying over a Body of Water", "creator": "Roman Odintsov", "page_url": "https://www.pexels.com/video/dragonflies-flying-over-a-body-of-water-8745453/", "download_url": "https://videos.pexels.com/video-files/8745453/8745453-uhd_4096_2160_30fps.mp4", "license": "Pexels License; free use and modification; attribution not required. Shows modern dragonflies, not Meganeura."}
        ],
        "generated_media": [
            {"filename": "reconstruccion-carbonifero-meganeura-01.png", "creator": "OpenAI image generation", "license": "AI-generated artistic reconstruction for this project; not documentary evidence.", "prompt_summary": "Meganeura-like griffinfly above a humid Carboniferous swamp forest."},
            {"filename": "reconstruccion-carbonifero-meganeura-02.png", "creator": "OpenAI image generation", "license": "AI-generated artistic reconstruction for this project; not documentary evidence.", "prompt_summary": "Close scientific-style artistic reconstruction of Meganeura in a Carboniferous forest."}
        ],
        "cta": "Si te gustan estos datos, dale like y suscríbete.",
        "social_caption": "Hace unos 300 millones de años, Meganeura podía alcanzar unos 70 cm de envergadura. La comparación está a escala con una persona y una libélula actual.\n\n#Carbonifero #Meganeura #InsectosGigantes #Prehistoria #Paleontologia #Ciencia #Reels #Shorts #TikTok"
    },
    "arthropleura": {
        "topic": "Arthropleura: el gigante que parecía un ciempiés",
        "aliases": ["arthropleura", "artropleura", "ciempiés gigante del carbonífero", "animal como un ciempiés del carbonífero"],
        "niche": "ciencia y prehistoria",
        "locale": "es-CO",
        "hook": "¡Este gigante del Carbonífero podía medir más que una persona!",
        "sources": [
            {"source_id": "src-nhm-arthropleura-head", "title": "Largest ever millipede’s head revealed by 300-million-year-old fossils", "publisher": "Natural History Museum", "author": "Josh Davis", "url": "https://www.nhm.ac.uk/discover/news/2024/october/largest-ever-millipede-head-revealed.html", "retrieved_at": "2026-10-07", "license_or_terms": "Referencia informativa; no se reutilizan imágenes.", "notes": "Arthropleura vivió hace más de 300 millones de años; estimaciones la sitúan hasta unos 2,6 m. Su anatomía combina rasgos de milpiés y ciempiés; dos pares de patas por segmento. No hay evidencia de patas especializadas para capturar presas."},
            {"source_id": "src-science-arthropleura-phylogeny", "title": "Head anatomy and phylogenomics show the Carboniferous giant Arthropleura belonged to a millipede-centipede group", "publisher": "Science Advances", "author": "Davies et al.", "url": "https://doi.org/10.1126/sciadv.adp6362", "retrieved_at": "2026-10-07", "license_or_terms": "Referencia científica; no se reutilizan figuras.", "notes": "Estudio sobre la anatomía cefálica y la posición evolutiva de Arthropleura."}
        ],
        "claims": [
            {"claim_id": "c1", "text": "Arthropleura vivió hace más de 300 millones de años y algunas estimaciones sugieren una longitud de hasta unos 2,6 metros.", "source_ids": ["src-nhm-arthropleura-head"], "status": "verified"},
            {"claim_id": "c2", "text": "Su anatomía combina rasgos de milpiés y ciempiés; tenía dos pares de patas por segmento.", "source_ids": ["src-nhm-arthropleura-head", "src-science-arthropleura-phylogeny"], "status": "verified"},
            {"claim_id": "c3", "text": "Los fósiles no muestran patas especializadas para atrapar presas; su dieta exacta sigue siendo incierta.", "source_ids": ["src-nhm-arthropleura-head"], "status": "verified"},
            {"claim_id": "c4", "text": "Arthropleura habitó bosques pantanosos del Carbonífero.", "source_ids": ["src-nhm-arthropleura-head"], "status": "verified"}
        ],
        "script": [
            {"scene_id": "s1", "claim_ids": ["c1"], "narration": "¡Mira esta comparación! Arthropleura podía medir hasta dos coma seis metros.", "caption": "", "duration_seconds": 5.0},
            {"scene_id": "s2", "claim_ids": ["c1", "c4"], "narration": "Vivió hace más de 300 millones de años, entre pantanos y helechos gigantes.", "caption": "Un gigante de los bosques pantanosos"},
            {"scene_id": "s3", "claim_ids": ["c2"], "narration": "No era un ciempiés moderno: combinaba rasgos de milpiés y ciempiés.", "caption": "Un pariente antiguo con rasgos de ambos"},
            {"scene_id": "s4", "claim_ids": ["c2"], "narration": "Y tenía dos pares de patas por cada segmento del cuerpo.", "caption": "Dos pares de patas por segmento"},
            {"scene_id": "s5", "claim_ids": ["c3"], "narration": "Aunque imponía, no hay señales de patas para atrapar presas. Su dieta aún es un misterio.", "caption": "Gigante, pero no hay pruebas de que cazara"},
            {"scene_id": "cta-subscribe", "claim_ids": [], "narration": "Si te gustan los animales sorprendentes, dale like y suscríbete.", "caption": "Dale like y suscríbete", "purpose": "channel_subscribe_cta"}
        ],
        "source_clip_plan": [
            {"scene_id": "s1", "filename": "apertura-comparacion-arthropleura.png", "effect": "hold"},
            {"scene_id": "s2", "filename": "reconstruccion-arthropleura-pantano.png"},
            {"scene_id": "s3", "filename": "milipedo-pexels-cerca.mp4", "at_ratio": 0.25},
            {"scene_id": "s4", "filename": "reconstruccion-arthropleura-detalle.png"},
            {"scene_id": "s5", "filename": "milipedo-pexels-terreno.mp4", "at_ratio": 0.60},
            {"scene_id": "cta-subscribe", "filename": "reconstruccion-arthropleura-pantano.png"}
        ],
        "stock_media": [
            {"filename": "milipedo-pexels-cerca.mp4", "platform": "Pexels", "title": "Millipede Crawling Close up", "creator": "Gilmer Diaz Estela", "page_url": "https://www.pexels.com/video/millipede-crawling-close-up-6252272/", "download_url": "https://videos.pexels.com/video-files/6252272/6252272-hd_1920_1080_30fps.mp4", "license": "Pexels License; free use and modification; attribution not required. Modern millipede used only as a visual analogue, not Arthropleura."},
            {"filename": "milipedo-pexels-terreno.mp4", "platform": "Pexels", "title": "Close up Footage of a Millipede", "creator": "Rahul Gautam", "page_url": "https://www.pexels.com/video/close-up-footage-of-a-millipede-5010345/", "download_url": "https://videos.pexels.com/video-files/5010345/5010345-hd_1920_1080_30fps.mp4", "license": "Pexels License; free use and modification; attribution not required. Modern millipede used only as a visual analogue, not Arthropleura."}
        ],
        "generated_media": [
            {"filename": "apertura-comparacion-arthropleura.png", "creator": "OpenAI image generation", "license": "AI-generated artistic scale illustration based on fossil estimates; not documentary evidence.", "prompt_summary": "3D comparison infographic: Arthropleura estimated up to 2.6 m versus 1.70 m person, with explanatory Spanish labels."},
            {"filename": "reconstruccion-arthropleura-pantano.png", "creator": "OpenAI image generation", "license": "AI-generated artistic reconstruction; not documentary evidence.", "prompt_summary": "Arthropleura in a Carboniferous swamp forest."},
            {"filename": "reconstruccion-arthropleura-detalle.png", "creator": "OpenAI image generation", "license": "AI-generated artistic reconstruction; not documentary evidence.", "prompt_summary": "Close detail of Arthropleura's armored segments and many legs."}
        ],
        "cta": "Si te gustan los animales sorprendentes, dale like y suscríbete.",
        "social_caption": "Arthropleura no era un ciempiés moderno: este enorme miriápodo del Carbonífero pudo alcanzar unos 2,6 metros, según algunas estimaciones. Su parentesco combina rasgos de milpiés y ciempiés.\n\n#Arthropleura #Carbonifero #Prehistoria #Paleontologia #Ciencia #AnimalesAsombrosos #Reels #Shorts #TikTok"
    }
}


IDEAS.update({'colibri': {'topic': 'Colibrí: 75 aleteos por segundo',
             'aliases': ['colibrí', 'colibri', 'hummingbird'],
             'niche': 'animales y naturaleza',
             'locale': 'es-CO',
             'hook': '¿Cómo puede quedarse quieto en el aire un ave tan pequeña?',
             'sources': [{'source_id': 'src-1',
                          'title': 'Singing Wings - Behavior',
                          'publisher': 'Bird Academy, Cornell Lab of Ornithology',
                          'author': 'Bird Academy, Cornell Lab of Ornithology',
                          'url': 'https://academy.allaboutbirds.org/singing-wings-behavior/',
                          'retrieved_at': '2026-10-11',
                          'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                          'notes': 'Sus alas baten entre 50 y 75 veces por segundo cerca de un comedero.'},
                         {'source_id': 'src-2',
                          'title': 'Broad-tailed Hummingbird Life History',
                          'publisher': 'Cornell Lab of Ornithology',
                          'author': 'Cornell Lab of Ornithology',
                          'url': 'https://www.allaboutbirds.org/guide/Broad-tailed_Hummingbird/lifehistory',
                          'retrieved_at': '2026-10-11',
                          'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                          'notes': 'El vuelo suspendido exige un rápido batir de alas.'},
                         {'source_id': 'src-3',
                          'title': 'Jumpstart Your Feeder Bird Knowledge',
                          'publisher': 'Bird Academy, Cornell Lab of Ornithology',
                          'author': 'Bird Academy, Cornell Lab of Ornithology',
                          'url': 'https://academy.allaboutbirds.org/jumpstart-your-feeder-bird-knowledge/',
                          'retrieved_at': '2026-10-11',
                          'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                          'notes': 'El vuelo estacionario requiere una fuente casi constante de néctar.'}],
             'claims': [{'claim_id': 'c1',
                         'text': 'Sus alas baten entre 50 y 75 veces por segundo cerca de un comedero.',
                         'source_ids': ['src-1'],
                         'status': 'verified'},
                        {'claim_id': 'c2',
                         'text': 'Al volar cerca de un comedero, sus alas pueden batir entre cincuenta y setenta y '
                                 'cinco veces por segundo.',
                         'source_ids': ['src-1'],
                         'status': 'verified'},
                        {'claim_id': 'c3',
                         'text': 'Ese movimiento rapidísimo le permite mantenerse suspendido frente a una flor.',
                         'source_ids': ['src-2'],
                         'status': 'verified'},
                        {'claim_id': 'c4',
                         'text': 'El vuelo exige tanta energía que necesita alimentarse con frecuencia de néctar.',
                         'source_ids': ['src-3'],
                         'status': 'verified'}],
             'script': [{'scene_id': 's1',
                         'claim_ids': ['c1'],
                         'narration': 'Hasta setenta y cinco aleteos por segundo: así se sostiene un colibrí en el '
                                      'aire.',
                         'caption': '',
                         'duration_seconds': 5.0},
                        {'scene_id': 's2',
                         'claim_ids': ['c2'],
                         'narration': 'Al volar cerca de un comedero, sus alas pueden batir entre cincuenta y setenta '
                                      'y cinco veces por segundo.',
                         'caption': 'Hasta 75 aleteos por segundo'},
                        {'scene_id': 's3',
                         'claim_ids': ['c3'],
                         'narration': 'Ese movimiento rapidísimo le permite mantenerse suspendido frente a una flor.',
                         'caption': 'Puede quedarse suspendido'},
                        {'scene_id': 's4',
                         'claim_ids': ['c4'],
                         'narration': 'El vuelo exige tanta energía que necesita alimentarse con frecuencia de néctar.',
                         'caption': 'Vuelo de alto consumo energético'},
                        {'scene_id': 'cta-subscribe',
                         'claim_ids': [],
                         'narration': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el '
                                      'próximo video.',
                         'caption': 'Dale like y suscríbete',
                         'purpose': 'channel_subscribe_cta'}],
             'source_clip_plan': [{'scene_id': 's1', 'filename': 'apertura-infografica.png', 'effect': 'hold'},
                                  {'scene_id': 's2', 'filename': 'colibri-hover.mp4', 'at_ratio': 0.25},
                                  {'scene_id': 's3', 'filename': 'colibri-nektar.mp4', 'at_ratio': 0.55},
                                  {'scene_id': 's4', 'filename': 'colibri-hover.mp4', 'at_ratio': 0.65},
                                  {'scene_id': 'cta-subscribe', 'filename': 'colibri-nektar.mp4', 'at_ratio': 0.65}],
             'stock_media': [{'filename': 'colibri-hover.mp4',
                              'platform': 'Pexels',
                              'title': 'A Humming Bird Suspended In The Air Flying Before Resting',
                              'creator': 'K',
                              'page_url': 'https://www.pexels.com/video/a-humming-bird-suspended-in-the-air-flying-before-resting-2908583/',
                              'download_url': 'https://videos.pexels.com/video-files/2908583/2908583-uhd_4096_2160_24fps.mp4',
                              'license': 'Pexels License; Pexels marca el clip como Free. En el video de tortuga laúd, '
                                         'las tomas son genéricas de tortugas marinas y no identifican especie.'},
                             {'filename': 'colibri-nektar.mp4',
                              'platform': 'Pexels',
                              'title': 'Humming Bird',
                              'creator': 'K',
                              'page_url': 'https://www.pexels.com/video/humming-bird-2402370/',
                              'download_url': 'https://videos.pexels.com/video-files/2402370/2402370-hd_1920_1080_24fps.mp4',
                              'license': 'Pexels License; Pexels marca el clip como Free. En el video de tortuga laúd, '
                                         'las tomas son genéricas de tortugas marinas y no identifican especie.'}],
             'generated_media': [{'filename': 'apertura-infografica.png',
                                  'creator': 'Ilustración 3D estilizada generada para esta producción',
                                  'license': 'Arte original creado para el video; no es fotografía documental.',
                                  'prompt_summary': 'HASTA 75 ALETEOS / SEGUNDO con ilustración del animal y diseño '
                                                    'vertical 9:16.'}],
             'cta': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el próximo video.',
             'social_caption': 'El colibrí puede batir sus alas hasta 75 veces por segundo y quedarse suspendido '
                               'frente a una flor. Ese vuelo consume mucha energía, por eso necesita buscar néctar con '
                               'frecuencia.\n'
                               '\n'
                               '#Colibri #Aves #Naturaleza #Ciencia #DatosCuriosos #Reels #Shorts #TikTok'},
 'casuario': {'topic': 'Casuario: el gigante que planta bosques',
              'aliases': ['casuario', 'cassowary'],
              'niche': 'animales y naturaleza',
              'locale': 'es-CO',
              'hook': 'Este ave puede medir casi lo mismo que una puerta y ayuda a sembrar la selva.',
              'sources': [{'source_id': 'src-1',
                           'title': 'Southern cassowary',
                           'publisher': 'Queensland Government',
                           'author': 'Queensland Government',
                           'url': 'https://www.qld.gov.au/environment/plants-animals/conservation/threatened-species/featured-projects/southern-cassowary',
                           'retrieved_at': '2026-10-11',
                           'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                           'notes': 'Las hembras pueden alcanzar hasta dos metros de altura.'},
                          {'source_id': 'src-2',
                           'title': 'Southern cassowaries: 10 facts',
                           'publisher': 'Queensland Department of Environment',
                           'author': 'Queensland Department of Environment',
                           'url': 'https://www.detsi.qld.gov.au/our-department/news-media/down-to-earth/cassowary-bird-facts',
                           'retrieved_at': '2026-10-11',
                           'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                           'notes': 'Dispersan semillas; el macho incuba los huevos y cuida a los polluelos.'}],
              'claims': [{'claim_id': 'c1',
                          'text': 'Las hembras pueden alcanzar hasta dos metros de altura.',
                          'source_ids': ['src-1'],
                          'status': 'verified'},
                         {'claim_id': 'c2',
                          'text': 'Las hembras de casuario austral pueden llegar a dos metros de altura.',
                          'source_ids': ['src-1'],
                          'status': 'verified'},
                         {'claim_id': 'c3',
                          'text': 'Al comer frutos y dispersar sus semillas, ayuda a regenerar la selva tropical.',
                          'source_ids': ['src-2'],
                          'status': 'verified'},
                         {'claim_id': 'c4',
                          'text': 'En esta especie, el macho incuba los huevos y se ocupa de las crías.',
                          'source_ids': ['src-2'],
                          'status': 'verified'}],
              'script': [{'scene_id': 's1',
                          'claim_ids': ['c1'],
                          'narration': 'Puede alcanzar dos metros: casi la altura de una puerta.',
                          'caption': '',
                          'duration_seconds': 5.0},
                         {'scene_id': 's2',
                          'claim_ids': ['c2'],
                          'narration': 'Las hembras de casuario austral pueden llegar a dos metros de altura.',
                          'caption': 'Hasta 2 metros de altura'},
                         {'scene_id': 's3',
                          'claim_ids': ['c3'],
                          'narration': 'Al comer frutos y dispersar sus semillas, ayuda a regenerar la selva tropical.',
                          'caption': 'Un jardinero gigante de la selva'},
                         {'scene_id': 's4',
                          'claim_ids': ['c4'],
                          'narration': 'En esta especie, el macho incuba los huevos y se ocupa de las crías.',
                          'caption': 'El macho cuida huevos y polluelos'},
                         {'scene_id': 'cta-subscribe',
                          'claim_ids': [],
                          'narration': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el '
                                       'próximo video.',
                          'caption': 'Dale like y suscríbete',
                          'purpose': 'channel_subscribe_cta'}],
              'source_clip_plan': [{'scene_id': 's1', 'filename': 'apertura-infografica.png', 'effect': 'hold'},
                                   {'scene_id': 's2', 'filename': 'casuario-playa.mp4', 'at_ratio': 0.25},
                                   {'scene_id': 's3', 'filename': 'casuarios-grupo.mp4', 'at_ratio': 0.55},
                                   {'scene_id': 's4', 'filename': 'casuario-playa.mp4', 'at_ratio': 0.65},
                                   {'scene_id': 'cta-subscribe', 'filename': 'casuarios-grupo.mp4', 'at_ratio': 0.65}],
              'stock_media': [{'filename': 'casuario-playa.mp4',
                               'platform': 'Pexels',
                               'title': 'A Cassowary Walking on the Seashore',
                               'creator': 'Peter Bekkers',
                               'page_url': 'https://www.pexels.com/video/a-cassowary-walking-on-the-seashore-5080103/',
                               'download_url': 'https://videos.pexels.com/video-files/5080103/5080103-hd_1920_1080_30fps.mp4',
                               'license': 'Pexels License; Pexels marca el clip como Free. En el video de tortuga '
                                          'laúd, las tomas son genéricas de tortugas marinas y no identifican '
                                          'especie.'},
                              {'filename': 'casuarios-grupo.mp4',
                               'platform': 'Pexels',
                               'title': 'Footage of group of wild cassowaries',
                               'creator': 'Magda Ehlers',
                               'page_url': 'https://www.pexels.com/video/footage-of-group-of-wild-cassowaries-9773728/',
                               'download_url': 'https://videos.pexels.com/video-files/9773728/9773728-uhd_3840_2160_30fps.mp4',
                               'license': 'Pexels License; Pexels marca el clip como Free. En el video de tortuga '
                                          'laúd, las tomas son genéricas de tortugas marinas y no identifican '
                                          'especie.'}],
              'generated_media': [{'filename': 'apertura-infografica.png',
                                   'creator': 'Ilustración 3D estilizada generada para esta producción',
                                   'license': 'Arte original creado para el video; no es fotografía documental.',
                                   'prompt_summary': 'HASTA 2 METROS DE ALTURA con ilustración del animal y diseño '
                                                     'vertical 9:16.'}],
              'cta': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el próximo video.',
              'social_caption': 'El casuario puede alcanzar dos metros y cumple un papel clave en la regeneración de '
                                'la selva: dispersa semillas grandes. Además, el macho incuba los huevos y cuida a las '
                                'crías.\n'
                                '\n'
                                '#Casuario #Selva #Aves #Naturaleza #DatosCuriosos #Reels #Shorts #TikTok'},
 'perezoso': {'topic': 'Perezoso: el almuerzo que tarda semanas',
              'aliases': ['perezoso', 'sloth'],
              'niche': 'animales y naturaleza',
              'locale': 'es-CO',
              'hook': 'En el cuerpo de un perezoso, una comida puede tardar semanas.',
              'sources': [{'source_id': 'src-1',
                           'title': 'Two-toed Sloth',
                           'publisher': 'Smithsonian’s National Zoo',
                           'author': 'Smithsonian’s National Zoo',
                           'url': 'https://nationalzoo.si.edu/animals/two-toed-sloth',
                           'retrieved_at': '2026-10-11',
                           'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                           'notes': 'La digestión puede tardar aproximadamente un mes; el pelaje alberga algas y '
                                    'pequeños animales.'},
                          {'source_id': 'src-2',
                           'title': 'Why are Sloths So Slow? And Other Sloth Facts',
                           'publisher': 'Smithsonian’s National Zoo',
                           'author': 'Smithsonian’s National Zoo',
                           'url': 'https://nationalzoo.si.edu/animals/news/why-are-sloths-so-slow-and-other-sloth-facts',
                           'retrieved_at': '2026-10-11',
                           'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                           'notes': 'Suelen bajar a defecar una vez por semana y pueden nadar.'}],
              'claims': [{'claim_id': 'c1',
                          'text': 'La digestión puede tardar aproximadamente un mes; el pelaje alberga algas y '
                                  'pequeños animales.',
                          'source_ids': ['src-1'],
                          'status': 'verified'},
                         {'claim_id': 'c2',
                          'text': 'Su metabolismo es tan lento que la comida puede tardar cerca de un mes en pasar por '
                                  'su tracto digestivo.',
                          'source_ids': ['src-1'],
                          'status': 'verified'},
                         {'claim_id': 'c3',
                          'text': 'Normalmente baja del árbol para defecar alrededor de una vez por semana.',
                          'source_ids': ['src-2'],
                          'status': 'verified'},
                         {'claim_id': 'c4',
                          'text': 'Su pelaje alberga algas, polillas y otros pequeños organismos.',
                          'source_ids': ['src-1'],
                          'status': 'verified'},
                         {'claim_id': 'c5',
                          'text': 'Y aunque se mueve despacio en tierra, también es un nadador competente.',
                          'source_ids': ['src-2'],
                          'status': 'verified'}],
              'script': [{'scene_id': 's1',
                          'claim_ids': ['c1'],
                          'narration': 'Una comida puede tardar hasta un mes en recorrer su sistema digestivo.',
                          'caption': '',
                          'duration_seconds': 5.0},
                         {'scene_id': 's2',
                          'claim_ids': ['c2'],
                          'narration': 'Su metabolismo es tan lento que la comida puede tardar cerca de un mes en '
                                       'pasar por su tracto digestivo.',
                          'caption': 'Hasta un mes digiriendo'},
                         {'scene_id': 's3',
                          'claim_ids': ['c3'],
                          'narration': 'Normalmente baja del árbol para defecar alrededor de una vez por semana.',
                          'caption': 'Baja del árbol una vez por semana'},
                         {'scene_id': 's4',
                          'claim_ids': ['c4'],
                          'narration': 'Su pelaje alberga algas, polillas y otros pequeños organismos.',
                          'caption': 'Su pelaje es un pequeño ecosistema'},
                         {'scene_id': 's5',
                          'claim_ids': ['c5'],
                          'narration': 'Y aunque se mueve despacio en tierra, también es un nadador competente.',
                          'caption': 'Lento en tierra; buen nadador'},
                         {'scene_id': 'cta-subscribe',
                          'claim_ids': [],
                          'narration': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el '
                                       'próximo video.',
                          'caption': 'Dale like y suscríbete',
                          'purpose': 'channel_subscribe_cta'}],
              'source_clip_plan': [{'scene_id': 's1', 'filename': 'apertura-infografica.png', 'effect': 'hold'},
                                   {'scene_id': 's2', 'filename': 'perezoso-trepando.mp4', 'at_ratio': 0.25},
                                   {'scene_id': 's3', 'filename': 'perezoso-curioso.mp4', 'at_ratio': 0.55},
                                   {'scene_id': 's4', 'filename': 'perezoso-trepando.mp4', 'at_ratio': 0.65},
                                   {'scene_id': 's5', 'filename': 'perezoso-curioso.mp4', 'at_ratio': 0.65},
                                   {'scene_id': 'cta-subscribe',
                                    'filename': 'perezoso-trepando.mp4',
                                    'at_ratio': 0.65}],
              'stock_media': [{'filename': 'perezoso-trepando.mp4',
                               'platform': 'Pexels',
                               'title': 'A Sloth Climbing a Tree',
                               'creator': 'Steven HAuse',
                               'page_url': 'https://www.pexels.com/video/a-sloth-climbing-a-tree-13899298/',
                               'download_url': 'https://videos.pexels.com/video-files/13899298/13899298-hd_1920_1080_30fps.mp4',
                               'license': 'Pexels License; Pexels marca el clip como Free. En el video de tortuga '
                                          'laúd, las tomas son genéricas de tortugas marinas y no identifican '
                                          'especie.'},
                              {'filename': 'perezoso-curioso.mp4',
                               'platform': 'Pexels',
                               'title': 'A Curious Sloth Hanging from a Tree Branch',
                               'creator': 'Steven HAuse',
                               'page_url': 'https://www.pexels.com/video/a-curious-sloth-hanging-from-a-tree-branch-13899360/',
                               'download_url': 'https://videos.pexels.com/video-files/13899360/13899360-hd_1920_1080_30fps.mp4',
                               'license': 'Pexels License; Pexels marca el clip como Free. En el video de tortuga '
                                          'laúd, las tomas son genéricas de tortugas marinas y no identifican '
                                          'especie.'}],
              'generated_media': [{'filename': 'apertura-infografica.png',
                                   'creator': 'Ilustración 3D estilizada generada para esta producción',
                                   'license': 'Arte original creado para el video; no es fotografía documental.',
                                   'prompt_summary': 'HASTA 1 MES DIGIRIENDO con ilustración del animal y diseño '
                                                     'vertical 9:16.'}],
              'cta': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el próximo video.',
              'social_caption': 'El metabolismo del perezoso es tan lento que la comida puede tardar cerca de un mes '
                                'en recorrer su sistema digestivo. Su pelaje alberga algas y pequeños animales: un '
                                'ecosistema diminuto.\n'
                                '\n'
                                '#Perezoso #Fauna #Naturaleza #Ciencia #DatosCuriosos #Reels #Shorts #TikTok'},
 'tortuga-laud': {'topic': 'Tortuga laúd: buceadora de las profundidades',
                  'aliases': ['tortuga laúd', 'tortuga laud', 'leatherback turtle'],
                  'niche': 'animales y naturaleza',
                  'locale': 'es-CO',
                  'hook': 'Una tortuga marina puede bajar a profundidades que superan un kilómetro.',
                  'sources': [{'source_id': 'src-1',
                               'title': 'Leatherback Turtle',
                               'publisher': 'NOAA Fisheries',
                               'author': 'NOAA Fisheries',
                               'url': 'https://www.fisheries.noaa.gov/species/leatherback-turtle',
                               'retrieved_at': '2026-10-11',
                               'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                               'notes': 'Bucea cerca de 4,000 pies por hasta 85 minutos; algunas migraciones promedian '
                                        '3,700 millas por sentido.'},
                              {'source_id': 'src-2',
                               'title': 'What is the largest sea turtle?',
                               'publisher': 'NOAA Ocean Service',
                               'author': 'NOAA Ocean Service',
                               'url': 'https://oceanservice.noaa.gov/facts/leatherback.html',
                               'retrieved_at': '2026-10-11',
                               'license_or_terms': 'Referencia factual; no se reutilizan imágenes.',
                               'notes': 'La tortuga laúd es la mayor tortuga marina viva.'}],
                  'claims': [{'claim_id': 'c1',
                              'text': 'Bucea cerca de 4,000 pies por hasta 85 minutos; algunas migraciones promedian '
                                      '3,700 millas por sentido.',
                              'source_ids': ['src-1'],
                              'status': 'verified'},
                             {'claim_id': 'c2',
                              'text': 'Eso equivale a unos mil doscientos metros, más profundo que cualquier otra '
                                      'tortuga.',
                              'source_ids': ['src-1'],
                              'status': 'verified'},
                             {'claim_id': 'c3',
                              'text': 'Algunas pueden permanecer bajo el agua hasta ochenta y cinco minutos.',
                              'source_ids': ['src-1'],
                              'status': 'verified'},
                             {'claim_id': 'c4',
                              'text': 'Sus migraciones pueden promediar tres mil setecientas millas en cada sentido.',
                              'source_ids': ['src-1'],
                              'status': 'verified'},
                             {'claim_id': 'c5',
                              'text': 'Su cubierta no es rígida: es resistente y flexible.',
                              'source_ids': ['src-1'],
                              'status': 'verified'}],
                  'script': [{'scene_id': 's1',
                              'claim_ids': ['c1'],
                              'narration': 'La tortuga laúd puede bucear cerca de cuatro mil pies de profundidad.',
                              'caption': '',
                              'duration_seconds': 5.0},
                             {'scene_id': 's2',
                              'claim_ids': ['c2'],
                              'narration': 'Eso equivale a unos mil doscientos metros, más profundo que cualquier otra '
                                           'tortuga.',
                              'caption': 'Cerca de 1.200 m bajo el mar'},
                             {'scene_id': 's3',
                              'claim_ids': ['c3'],
                              'narration': 'Algunas pueden permanecer bajo el agua hasta ochenta y cinco minutos.',
                              'caption': 'Hasta 85 minutos sumergida'},
                             {'scene_id': 's4',
                              'claim_ids': ['c4'],
                              'narration': 'Sus migraciones pueden promediar tres mil setecientas millas en cada '
                                           'sentido.',
                              'caption': 'Más de 5.900 km por trayecto'},
                             {'scene_id': 's5',
                              'claim_ids': ['c5'],
                              'narration': 'Su cubierta no es rígida: es resistente y flexible.',
                              'caption': 'Cubierta flexible, no placas duras'},
                             {'scene_id': 'cta-subscribe',
                              'claim_ids': [],
                              'narration': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte '
                                           'el próximo video.',
                              'caption': 'Dale like y suscríbete',
                              'purpose': 'channel_subscribe_cta'}],
                  'source_clip_plan': [{'scene_id': 's1', 'filename': 'apertura-infografica.png', 'effect': 'hold'},
                                       {'scene_id': 's2', 'filename': 'tortuga-arrecife.mp4', 'at_ratio': 0.25},
                                       {'scene_id': 's3', 'filename': 'tortuga-oceano.mp4', 'at_ratio': 0.55},
                                       {'scene_id': 's4', 'filename': 'tortuga-arrecife.mp4', 'at_ratio': 0.65},
                                       {'scene_id': 's5', 'filename': 'tortuga-oceano.mp4', 'at_ratio': 0.65},
                                       {'scene_id': 'cta-subscribe',
                                        'filename': 'tortuga-arrecife.mp4',
                                        'at_ratio': 0.65}],
                  'stock_media': [{'filename': 'tortuga-arrecife.mp4',
                                   'platform': 'Pexels',
                                   'title': 'Marine Turtle Swimming Amongst Coral Reefs',
                                   'creator': 'JUN HO LEE',
                                   'page_url': 'https://www.pexels.com/video/marine-turtle-swimming-amongst-coral-reefs-32997245/',
                                   'download_url': 'https://videos.pexels.com/video-files/32997245/14063185_1920_1080_60fps.mp4',
                                   'license': 'Pexels License; Pexels marca el clip como Free. En el video de tortuga '
                                              'laúd, las tomas son genéricas de tortugas marinas y no identifican '
                                              'especie.'},
                                  {'filename': 'tortuga-oceano.mp4',
                                   'platform': 'Pexels',
                                   'title': 'Turtle Swimming in the Ocean',
                                   'creator': 'Zlatin Georgiev',
                                   'page_url': 'https://www.pexels.com/video/turtle-swimming-in-the-ocean-7173031/',
                                   'download_url': 'https://videos.pexels.com/video-files/7173031/7173031-uhd_3840_2160_25fps.mp4',
                                   'license': 'Pexels License; Pexels marca el clip como Free. En el video de tortuga '
                                              'laúd, las tomas son genéricas de tortugas marinas y no identifican '
                                              'especie.'}],
                  'generated_media': [{'filename': 'apertura-infografica.png',
                                       'creator': 'Ilustración 3D estilizada generada para esta producción',
                                       'license': 'Arte original creado para el video; no es fotografía documental.',
                                       'prompt_summary': 'CASI 1.200 METROS DE BUCEO con ilustración del animal y '
                                                         'diseño vertical 9:16.'}],
                  'cta': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el próximo video.',
                  'social_caption': 'La tortuga laúd puede bucear cerca de 1.200 metros y permanecer sumergida hasta '
                                    '85 minutos. Algunas recorren más de 5.900 kilómetros por trayecto. Los clips son '
                                    'de tortugas marinas genéricas y no confirman que sean laúd.\n'
                                    '\n'
                                    '#TortugaLaud #Oceano #VidaMarina #Naturaleza #Ciencia #DatosCuriosos #Reels '
                                    '#Shorts #TikTok'}} )


# Media corrections for the four October 11 deliveries.
IDEAS['casuario']['stock_media'][1] = {'filename':'casuarios-grupo.mp4','platform':'Pexels','title':'Southern Cassowary','creator':'Mikhail Nilov','page_url':'https://www.pexels.com/video/southern-cassowary-7723100/','download_url':'https://videos.pexels.com/video-files/7723100/7723100-hd_1920_1080_25fps.mp4','license':'Pexels License; page marked Free; confirmed Southern Cassowary footage.'}

# Topic-specific image content lives beside the catalog claims. The image
# builder reads the channel-wide visual identity from estilo_infografia_3d.md.
IDEAS['colibri']['opening_visual'] = {
    'protagonist': 'colibrí de plumaje iridiscente suspendido junto a una flor',
    'title': '¿ALAS CASI INVISIBLES?',
    'main_claim_id': 'c1',
    'environment': 'bosque nuboso andino con flores tropicales al amanecer',
    'question': '¿Cómo logra quedarse quieto en el aire?'
}
IDEAS['casuario']['opening_visual'] = {
    'protagonist': 'hembra de casuario austral adulta, con casco y plumaje negro detallado',
    'title': '¿MÁS ALTA QUE TÚ?',
    'main_claim_id': 'c1',
    'environment': 'selva tropical húmeda australiana, con luz cinematográfica filtrada por las hojas',
    'comparison': 'Mostrar una hembra de hasta 2 m junto a una persona adulta de referencia de 1,70 m; mismo suelo, escala proporcional y comparación claramente ilustrativa.',
    'question': '¿Qué otros gigantes viven en la selva?'
}
IDEAS['perezoso']['opening_visual'] = {
    'protagonist': 'perezoso de tres dedos colgado de una rama, con pelaje y garras muy detallados',
    'title': 'UN ALMUERZO LENTÍSIMO',
    'main_claim_id': 'c1',
    'environment': 'dosel de una selva tropical con luz dorada, hojas y ramas húmedas',
    'question': '¿Te imaginas tardar tanto en digerir?'
}
IDEAS['tortuga-laud']['opening_visual'] = {
    'protagonist': 'tortuga laúd adulta con caparazón de crestas flexibles y aletas largas',
    'title': 'LA BUCEADORA DEL ABISMO',
    'main_claim_id': 'c2',
    'environment': 'océano azul profundo con rayos cian que se desvanecen hacia el abismo',
    'question': '¿Qué encontrará a esa profundidad?'
}

for _k, _prompt_summary in {
    'colibri': 'Colibrí en bosque nuboso; usar datos verificados de aleteo, vuelo suspendido y energía.',
    'casuario': 'Hembra de casuario austral y referencia humana a escala proporcional; altura verificada.',
    'perezoso': 'Pérezoso en dosel de selva; datos verificados de digestión, descenso semanal y nado.',
    'tortuga-laud': 'Tortuga laúd en océano profundo; profundidad, inmersión y migración respaldadas por fuentes.'
}.items():
    IDEAS[_k]['generated_media'] = [{
        'filename': 'apertura-infografica.png',
        'creator': 'OpenAI image generation; rótulos añadidos por código',
        'license': 'Ilustración generada para este video; no es metraje documental. Revisar términos antes de publicar.',
        'prompt_summary': _prompt_summary
    }]


for _k in ('colibri','casuario','perezoso','tortuga-laud'):
    IDEAS[_k]['source_clip_plan'][0]['effect'] = 'slow_centered_zoom'


IDEAS['ballena-azul'] = {
    'topic': 'Ballena azul: el animal más grande del planeta',
    'aliases': ['ballena azul', 'la ballena azul', 'blue whale'],
    'niche': 'animales y naturaleza',
    'locale': 'es-CO',
    'hook': 'La ballena azul es tan enorme que una persona a su lado parecería diminuta.',
    'sources': [
        {'source_id': 'src-noaa-blue-whale', 'title': 'Blue Whale: Resources', 'publisher': 'NOAA Fisheries', 'author': 'NOAA Fisheries', 'url': 'https://www.fisheries.noaa.gov/species/blue-whale/resources', 'retrieved_at': '2026-10-11', 'license_or_terms': 'Referencia factual; no se reutilizan sus imágenes.', 'notes': 'Confirma que es el animal más grande conocido, se alimenta principalmente de krill y filtra agua mediante barbas.'},
        {'source_id': 'src-nhm-blue-whale-record-breaker', 'title': 'The life of the blue whale: Record breaker', 'publisher': 'Natural History Museum, London', 'author': 'Natural History Museum', 'url': 'https://www.nhm.ac.uk/bluewhale/ocean/record-breaker/', 'retrieved_at': '2026-10-11', 'license_or_terms': 'Referencia factual; no se reutilizan sus imágenes.', 'notes': 'Informa longitudes de hasta 30 m y pesos de hasta 180 toneladas, con la salvedad de que la mayoría pesa menos.'},
        {'source_id': 'src-wdc-blue-whale-facts', 'title': 'Facts about blue whales', 'publisher': 'Whale and Dolphin Conservation', 'author': 'WDC', 'url': 'https://us.whales.org/whales-dolphins/facts-about-blue-whales/', 'retrieved_at': '2026-10-11', 'license_or_terms': 'Referencia factual; no se reutilizan sus imágenes.', 'notes': 'Describe el corazón de 180 kg como dato aproximado y su dieta de krill filtrado con barbas.'}
    ],
    'claims': [
        {'claim_id': 'c1', 'text': 'La ballena azul es el animal más grande conocido que ha vivido en la Tierra.', 'source_ids': ['src-noaa-blue-whale'], 'status': 'verified'},
        {'claim_id': 'c2', 'text': 'Puede alcanzar unos 30 metros y hasta 180 toneladas, aunque la mayoría pesa menos.', 'source_ids': ['src-nhm-blue-whale-record-breaker'], 'status': 'verified', 'scope_note': 'Cifras máximas; no representan a la mayoría de individuos.'},
        {'claim_id': 'c3', 'text': 'El corazón de una ballena azul puede pesar cerca de 180 kg.', 'source_ids': ['src-wdc-blue-whale-facts'], 'status': 'verified', 'scope_note': 'Aproximación; el peso varía y la cifra no se presenta como valor exacto de todos los individuos.'},
        {'claim_id': 'c4', 'text': 'Se alimenta sobre todo de krill y lo filtra del agua con sus barbas.', 'source_ids': ['src-noaa-blue-whale', 'src-wdc-blue-whale-facts'], 'status': 'verified'}
    ],
    'script': [
        {'scene_id': 's1', 'claim_ids': ['c1'], 'narration': 'La ballena azul: el animal más grande que jamás ha existido.', 'caption': '', 'duration_seconds': 5.0},
        {'scene_id': 's2', 'claim_ids': ['c2'], 'narration': 'Puede alcanzar unos treinta metros y hasta ciento ochenta toneladas. A su lado, una persona parece diminuta.', 'caption': 'Hasta 30 metros y 180 toneladas'},
        {'scene_id': 's3', 'claim_ids': ['c3'], 'narration': 'Su corazón puede pesar cerca de ciento ochenta kilos: más que dos personas adultas juntas.', 'caption': 'Un corazón de cerca de 180 kg'},
        {'scene_id': 's4', 'claim_ids': ['c4'], 'narration': 'Y pese a su tamaño, se alimenta de krill diminuto, que filtra del agua con sus barbas.', 'caption': 'Filtra krill con sus barbas'},
    ],
    'source_clip_plan': [
        {'filename': 'infografia.png', 'effect': 'slow_centered_zoom'},
        {'filename': 'animate-the-blue-whale-and-the-man-slightly-breath.mp4', 'at_ratio': 0.14},
        {'filename': 'video-1056288514230625.mp4', 'at_ratio': 0.58},
        {'filename': 'video-1056288517563958.mp4', 'at_ratio': 0.82},
        {'filename': 'video-1056291647563645.mp4', 'at_ratio': 0.38},
    ],
    'cta': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el próximo video.',
    'opening_visual': {'protagonist': 'ballena azul de escala colosal junto a una persona buceadora', 'title': 'BALLENA AZUL: EL ANIMAL MÁS GRANDE DEL PLANETA', 'main_claim_id': 'c2', 'environment': 'océano azul profundo con rayos de luz', 'comparison': 'La persona debe verse a escala coherente frente a una ballena de hasta 30 metros.', 'question': '¿Te imaginas nadar junto a un gigante así?'},
    'social_caption': 'La ballena azul puede alcanzar unos 30 metros y su corazón rondar los 180 kg. Descubre cómo este gigante se alimenta de diminuto krill.\n\n#BallenaAzul #Oceano #VidaMarina #Naturaleza #Ciencia #DatosCuriosos #Reels #Shorts #TikTok'
}
IDEAS['ballena-azul']['generated_media'] = [{
    'filename': 'infografia.png',
    'creator': 'OpenAI image generation',
    'license': 'Ilustración generada para este video; no es metraje documental. Revisar términos antes de publicar.',
    'prompt_summary': 'Infografía vertical de ballena azul con comparación humana, barbas y datos de longitud, peso y corazón.'
}]


IDEAS['pez-cabeza-serpiente-aire'] = {
    'topic': 'Pez cabeza de serpiente: el pez que respira aire',
    'aliases': ['pez cabeza de serpiente respira aire', 'snakehead que respira aire', 'cabeza de serpiente fuera del agua'],
    'niche': 'animales y naturaleza',
    'locale': 'es-CO',
    'hook': 'No es una serpiente: es un pez capaz de respirar aire.',
    'sources': [
        {'source_id': 'src-usgs-northern-snakehead-profile', 'title': 'Northern Snakehead (Channa argus) - Species Profile', 'publisher': 'U.S. Geological Survey', 'author': 'USGS Nonindigenous Aquatic Species', 'url': 'https://nas.er.usgs.gov/queries/FactSheet.aspx?SpeciesID=2265', 'retrieved_at': '2026-10-11', 'license_or_terms': 'Referencia factual; no se reutilizan sus imágenes.', 'notes': 'La especie respira aire; puede sobrevivir fuera del agua hasta cuatro días, pero la migración terrestre es posible solo para juveniles.'},
        {'source_id': 'src-usgs-snakeheads-faq', 'title': 'What are snakeheads?', 'publisher': 'U.S. Geological Survey', 'author': 'USGS', 'url': 'https://www.usgs.gov/faqs/what-are-snakeheads', 'retrieved_at': '2026-10-11', 'license_or_terms': 'Referencia factual; no se reutilizan sus imágenes.', 'notes': 'Describe a los snakeheads como peces de agua dulce que respiran aire y señala riesgos potenciales al ser introducidos fuera de su área nativa.'},
        {'source_id': 'src-cdfw-snakehead', 'title': 'California’s Invaders: Snakehead', 'publisher': 'California Department of Fish and Wildlife', 'author': 'CDFW', 'url': 'https://wildlife.ca.gov/Conservation/Invasives/Species/Snakehead', 'retrieved_at': '2026-10-11', 'license_or_terms': 'Referencia factual; no se reutilizan sus imágenes.', 'notes': 'Explica el órgano suprabranquial, respiración aérea, condición de humedad para sobrevivir fuera del agua, impactos potenciales y que algunas especies pueden desplazarse en tierra.'},
        {'source_id': 'src-ontario-northern-snakehead', 'title': 'Northern Snakehead (Channa argus)', 'publisher': 'Government of Ontario', 'author': 'Ontario Ministry of Natural Resources', 'url': 'https://www.ontario.ca/files/2025-07/stdprod-100631.pdf', 'retrieved_at': '2026-10-11', 'license_or_terms': 'Referencia factual; no se reutilizan sus imágenes.', 'notes': 'Indica longitud de hasta 85 cm y peso de hasta 7 kg para la cabeza de serpiente del norte.'}
    ],
    'claims': [
        {'claim_id': 'c1', 'text': 'La cabeza de serpiente del norte (Channa argus) es un pez de agua dulce que respira aire.', 'source_ids': ['src-usgs-northern-snakehead-profile', 'src-usgs-snakeheads-faq'], 'status': 'verified'},
        {'claim_id': 'c2', 'text': 'Puede sobrevivir hasta cuatro días fuera del agua si permanece húmeda.', 'source_ids': ['src-usgs-northern-snakehead-profile', 'src-cdfw-snakehead'], 'status': 'verified', 'scope_note': 'Máximo reportado; depende de condiciones, no significa que tolere secarse.'},
        {'claim_id': 'c3', 'text': 'Los desplazamientos terrestres de la cabeza de serpiente del norte son posibles en juveniles; los adultos tienen menor capacidad para migrar por tierra.', 'source_ids': ['src-usgs-northern-snakehead-profile'], 'status': 'verified'},
        {'claim_id': 'c4', 'text': 'Al ser introducida fuera de su área nativa, puede amenazar peces y ecosistemas locales.', 'source_ids': ['src-usgs-snakeheads-faq'], 'status': 'verified', 'scope_note': 'El riesgo depende del lugar y de la especie; no generalizar la condición invasora a su área nativa.'},
        {'claim_id': 'c5', 'text': 'La cabeza de serpiente del norte puede alcanzar unos 85 cm de longitud.', 'source_ids': ['src-ontario-northern-snakehead'], 'status': 'verified', 'scope_note': 'Longitud máxima reportada en la ficha del Gobierno de Ontario.'}
    ],
    'script': [
        {'scene_id': 's1', 'claim_ids': ['c1'], 'narration': 'No es una serpiente: es un pez capaz de respirar aire.', 'caption': '', 'duration_seconds': 5.0},
        {'scene_id': 's2', 'claim_ids': ['c1'], 'narration': 'La cabeza de serpiente del norte puede tomar oxígeno directamente del aire y soportar aguas con muy poco oxígeno.', 'caption': 'Respira aire y tolera poco oxígeno'},
        {'scene_id': 's3', 'claim_ids': ['c2'], 'narration': 'Si permanece húmeda, puede sobrevivir fuera del agua hasta cuatro días; eso no significa que pueda vivir seca.', 'caption': 'Hasta 4 días fuera del agua si sigue húmeda'},
        {'scene_id': 's4', 'claim_ids': ['c3'], 'narration': 'El detalle sorprendente: los juveniles pueden desplazarse por tierra húmeda, pero los adultos no hacen largas caminatas.', 'caption': 'El desplazamiento terrestre es de juveniles'},
        {'scene_id': 's5', 'claim_ids': ['c4'], 'narration': 'Y donde se introduce fuera de su región nativa, puede amenazar peces locales. Por eso nunca liberes un pez exótico.', 'caption': 'Introducirlo puede poner en riesgo ecosistemas'},
    ],
    'source_clip_plan': [
        {'filename': 'infografia.png', 'effect': 'slow_centered_zoom'},
        {'filename': '0204 (1)(3).mp4', 'at_ratio': 0.18},
        {'filename': 'nuevo-1.mp4', 'at_ratio': 0.42},
        {'filename': 'nuevo 2-1.mp4', 'at_ratio': 0.67},
        {'filename': 'cazando-1.mp4', 'at_ratio': 0.31},
        {'filename': 'Nuevo 3-1.mp4', 'at_ratio': 0.53},
    ],
    'cta': 'Si te gustan los datos curiosos, dale like y suscríbete para no perderte el próximo video.',
    'opening_visual': {'protagonist': 'cabeza de serpiente del norte (Channa argus), pez alargado de agua dulce con cabeza aplanada y patrón marrón oliva', 'title': 'PEZ CABEZA DE SERPIENTE: EL PEZ QUE RESPIRA AIRE', 'main_claim_id': 'c2', 'environment': 'laguna de agua dulce con vegetación y orilla húmeda', 'comparison': 'Mostrar un pez de hasta 85 cm junto a una persona de 1,70 m en escala proporcional; no mostrar a un adulto caminando por tierra.', 'question': '¿Cómo sobrevive fuera del agua?'},
    'generated_media': [{
        'filename': 'infografia.png',
        'creator': 'OpenAI image generation',
        'license': 'Ilustración generada para este video; no es metraje documental. Revisar términos antes de publicar.',
        'prompt_summary': 'Infografía vertical del cabeza de serpiente del norte con escala humana, respiración aérea y desplazamiento terrestre de juveniles.'
    }],
    'social_caption': 'No es una serpiente: el cabeza de serpiente del norte respira aire y, si permanece húmedo, puede sobrevivir fuera del agua varios días. El dato clave: los desplazamientos por tierra se asocian a juveniles.\n\n#PezCabezaDeSerpiente #ChannaArgus #Peces #Naturaleza #Ciencia #DatosCuriosos #Reels #Shorts #TikTok'
}
