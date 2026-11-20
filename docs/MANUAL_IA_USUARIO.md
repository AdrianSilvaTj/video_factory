# Video Factory — Manual para que una IA prepare las escenas de un video

> Estado documentado: rama `main` hasta el commit `4f108c4` (2 de noviembre de 2026). Describe la app **tal como está en el código**; si algún nombre de botón o campo no coincide con lo que ves en pantalla, confía en la pantalla y en el código (`video_factory/gui/studio.py`, `video_factory/gui/media_dialog.py`, `video_factory/project.py`) y no en este texto.
> Complementa `docs/CONTEXTO_PARA_IA.md`, que es para quien **desarrolla** la app. Este manual es para quien **la usa como ayudante**.

---

## 0. Tu tarea en una frase

**Crear las escenas del video (diálogo + imagen o video de cada una) y dejar el proyecto listo para que el usuario pulse «Renderizar video».**

### Flujo acordado con el usuario

- La IA crea el proyecto con el tema que indique el usuario y prepara sus escenas. Después, el usuario abre la aplicación y selecciona ese proyecto para revisar el trabajo realizado.
- La primera escena debe utilizar una infografía de apertura sobre el tema, siguiendo el diseño visual establecido para este proyecto: formato vertical 9:16, estilo hiperrealista y cinematográfico, protagonista dominante, cuatro etiquetas con título y subtítulo de dato curioso, y los elementos condicionados por el tema (por ejemplo, comparación humana cuando se solicite, o mapa y bandera cuando sea un lugar).
- Al menos una escena adicional debe incluir una imagen generada por la IA, hiperrealista, visualmente impactante y directamente relacionada con lo que se narra. Debe reforzar el dato o la situación de esa escena y conservar una composición apta para pantalla móvil.
- Las imágenes generadas deben evitar contenido gráfico o morboso, sangre, gore, violencia explícita, sexualización, desnudez, odio, acoso, instrucciones peligrosas, suplantación de personas reales, logotipos o marcas que puedan causar problemas de derechos. No presentar una recreación sintética como si fuera una fotografía documental real; si corresponde, dejar constancia de que es una ilustración generada por IA. Revisar siempre las políticas vigentes de YouTube antes de publicar; estas precauciones reducen riesgos, pero no garantizan la aprobación automática del video.
- En la carpeta del proyecto, la IA debe crear un archivo Markdown para la publicación, por ejemplo `descripcion_publicacion.md`. Debe contener una descripción llamativa del video con emojis y hashtags relevantes. Debajo de la descripción debe incluir un comentario independiente, redactado para que el usuario pueda copiarlo y fijarlo en el video, invitando a la audiencia a comentar.

### Lo que SÍ haces

- Escribir o adaptar el guion y repartirlo en escenas.
- Buscar y descargar los recursos visuales (videos e imágenes) y asignar uno a cada escena.
- Crear dentro de la carpeta del proyecto el archivo Markdown con la descripción de publicación y el comentario sugerido para fijar.
- Ajustar, si hace falta, las opciones **de cada escena** (encuadre, movimiento, subtítulos de la escena, texto en imagen, efectos, etc.; ver §4.5). Si el usuario no pidió nada especial, deja los valores por defecto.
- Hacer **vistas previas** de escenas para comprobar el resultado.
- Informar al usuario de lo que dejaste hecho y de cualquier aviso.

### Lo que NO haces (el usuario lo configura él mismo)

| No toques | Dónde está |
|---|---|
| **Formato** (vertical / horizontal) y **canal** | Pestaña «Proyecto» → «Formato y canal» |
| **Voz** y sus ajustes (velocidad, tono, volumen) | Pestaña «Voz» |
| **Música de fondo** (activar, volumen, archivo) | Pestaña «Música» |
| **Outro** (incluir, archivo) | Pestaña «Proyecto» → «Outro» |
| **Estilo de subtítulos** (fuente, tamaño, colores, negrita) | Pestaña «Subtítulos» |
| **Datos para YouTube** (título, descripción, etiquetas) | Pestaña «Proyecto» → «Datos para YouTube…» |
| Nombre del proyecto, ni crear/borrar/renombrar proyectos | — |
| **El render final**: **no pulses «Renderizar video» ni llames a `render_project()` sin `only_scenes`** | Lo hace el usuario |

Si crees que algo general está mal (por ejemplo, el formato es horizontal pero pediste imágenes verticales, o la voz no encaja con el tono), **no lo cambies: avísalo en tu informe** y deja que el usuario decida.

---

## 1. Qué es la app (contexto mínimo)

**Video Factory** (Windows, Python + PySide6 + FFmpeg) arma videos cortos **por escenas**. Cada escena tiene un **diálogo** que se convierte en voz neuronal y un **recurso visual** (imagen con movimiento opcional o clip de video). El proyecto tiene además voz, música, subtítulos y outro (los configura el usuario). Al renderizar, la app produce el video, los créditos de los recursos y los datos para YouTube.

La duración de una escena narrada = **duración de la voz + 0,35 s de pausa + «Tiempo extra»**. La app estima ≈ **2,6 palabras por segundo**.

### 1.1 Qué debes saber antes de empezar (pregúntalo si no está claro)

1. **¿Con qué proyecto trabajo?** El usuario ya lo creó y configuró. Pídele el nombre (o confirma cuál está abierto en la ventana). **No crees un proyecto nuevo** salvo que te lo pida expresamente.
2. **¿Cuál es el tema/guion?** Si te da el guion, úsalo tal cual (puedes dividirlo en escenas); si solo da el tema, propón el guion y espera su visto bueno si es largo o delicado.
3. **¿El proyecto ya tiene escenas?** Si ya hay escenas con contenido, **no las borres ni las reemplaces**; añade las tuyas al final salvo que el usuario diga otra cosa. Una única escena vacía inicial sí se puede reemplazar (la propia función «Pegar guion…» lo hace).
4. **Lee (sin cambiar) los ajustes del proyecto** para decidir bien: formato (vertical/horizontal), canal y voz. Con eso eliges la duración objetivo y el tipo de recursos (§3, §5).

**Regla de contenido:** no inventes datos. El guion debe poder respaldarse con fuentes; si dudas de un dato, no lo incluyas o márcalo al usuario.

---

## 2. Dos maneras de operar la app

| | **Ruta A — Interfaz gráfica** | **Ruta B — API de Python (sin ventana)** |
|---|---|---|
| Cuándo usarla | Tienes control de pantalla/ratón/teclado. **Es la ruta recomendada cuando el usuario ya tiene el proyecto abierto en la ventana.** | Solo si el usuario confirma que ese proyecto **no está abierto** en la ventana (ver aviso abajo). |
| Cómo | La app abierta (`python -m video_factory.gui` o el acceso directo «Video Factory») | Un script Python que importa `video_factory.project` y `video_factory.stock_sources` |

> **Aviso (Ruta B):** si el proyecto está abierto en la ventana y editas `project.json` por código, la app **sobrescribirá tus cambios** al autoguardar. Usa la Ruta B únicamente con la ventana cerrada (o con ese proyecto no abierto). Al terminar, el usuario abre el proyecto y verá tus escenas.

### 2.1 Requisitos del entorno (verifícalos primero)

- Windows 10/11 y **FFmpeg** accesible (en el PATH o instalado con winget como `Gyan.FFmpeg`).
- Entorno virtual en `video_factory\.venv`. Los comandos de este manual se ejecutan **desde la raíz del repositorio**, de preferencia con `video_factory\.venv\Scripts\python.exe`.
- `edge-tts` en `data\tts-packages`. Sin esa carpeta, las vistas previas con diálogo fallan con «Falta edge-tts en …».
- Claves de los bancos en `video_factory\.env` (`PEXELS_API_KEY`, `PIXABAY_API_KEY`, y opcionalmente `VECTEEZY_ACCOUNT_ID` / `VECTEEZY_API_KEY`). NASA, Wikimedia Commons y Openverse funcionan sin clave. **Nunca imprimas, copies ni envíes el contenido de `.env`.**
- Conexión a internet.

Comprobación rápida desde la raíz del repo:

```bash
video_factory/.venv/Scripts/python.exe -c "import PySide6, sys; print('PySide6 OK', sys.version.split()[0])"
ffmpeg -version
dir data\tts-packages
```

---

## 3. Preparar el guion y las escenas (antes de abrir nada)

Pauta según el formato del proyecto (que lees, no cambias):

- **Vertical (9:16):** objetivo de **45 s**, es decir ≈ 110–120 palabras en **6 a 10 escenas**, cada una de 1 o 2 frases (≈ 10–25 palabras, 4–9 s).
- **Horizontal (16:9):** no hay objetivo fijo; sigue la duración que pida el usuario (si no la dio, pregúntala).
- Una **apertura** que enganche (dato sorprendente o pregunta) y un **cierre** con invitación a seguir/comentar.
- Una idea visual clara por escena: será tu palabra de búsqueda (§5).
- **Capítulos de YouTube:** solo si el usuario los pidió, pon un título corto en el campo «capítulo» de las escenas que abren un tramo nuevo (mínimo 3 marcas, primera en 0:00, tramos de ≥ 10 s).

Formato del guion para la app: **un párrafo por escena, separados por una línea en blanco**.

```text
El jaguar es el felino más grande de América.

Su mordida es una de las más fuertes del reino animal: puede perforar el caparazón de una tortuga.

Vive desde México hasta el norte de Argentina, casi siempre cerca del agua.
```

---

## 4. Ruta A — Operar la interfaz gráfica

### 4.1 Mapa de la ventana

La ventana tiene tres columnas y un panel de mensajes:

| Zona | Contenido |
|---|---|
| **Izquierda** — pestañas | **Proyecto** · **Voz** · **Música** · **Subtítulos**. **Son los ajustes generales del usuario: puedes mirarlas, pero no cambies nada ahí.** |
| **Centro** — lista de escenas | Título «Escena N · ~X s», casilla «Vista previa», botones ↑ ↓ ✕, campo de capítulo, «Tiempo extra», cuadro de **diálogo** y un **botón-miniatura** (96×96) para elegir recurso. Arriba: «Pegar guion…». Abajo: «+ Añadir escena». |
| **Derecha** — detalle de la escena seleccionada | Vista del cuadro, «Elegir o cambiar imagen / video…», «▶ Vista previa de la escena», «↻ Volver a renderizar», pestañas **Imagen / video · Texto · Audio**, duración estimada, **«Renderizar video» (no lo pulses)** |
| **Abajo a la derecha** | **Panel de mensajes** (log). **Léelo después de cada acción importante.** |

La app **guarda sola** unos 0,5 s después de cada cambio. Hacer clic en una tarjeta de escena la selecciona y muestra sus opciones a la derecha.

> Mientras algo se procesa (voz, búsqueda, descarga, vista previa) la interfaz se bloquea y aparece una barra de progreso con «Cancelar». Espera a que termine antes de seguir.

### 4.2 Paso a paso

#### Paso 1 — Asegurar que estás en el proyecto correcto
- Confirma el nombre en el título de la ventana («Video Factory — <nombre>») y en el desplegable «Abrir:» de la pestaña Proyecto. **Si hay que abrir otro proyecto, elígelo en «Abrir:»; no uses «Nuevo proyecto…».**
- Mira (sin modificar) el formato de la pestaña Proyecto → «Formato y canal».

#### Paso 2 — Cargar el guion como escenas
**Opción recomendada:** botón **«Pegar guion…»** (arriba de la lista de escenas) → pega el guion con **una línea en blanco entre párrafos** → Aceptar. Cada párrafo se convierte en una escena. Si el proyecto solo tenía la escena vacía inicial, la reemplaza; si ya tiene escenas, añade las nuevas **al final**.

**Atención con el teclado:** dentro del cuadro de diálogo de una escena, **pulsar Enter parte la escena en dos** (lo que está tras el cursor pasa a una escena nueva). **No uses Enter para saltos de línea.** Para añadir una escena a mano usa **«+ Añadir escena»** (se inserta después de la seleccionada).

Otras acciones por escena: ↑ / ↓ para reordenar, ✕ para eliminar (pide confirmación; solo tus escenas), «Tiempo extra» para sumar segundos tras la narración y el campo de capítulo.

#### Paso 3 — Buscar y asignar el recurso visual de cada escena
Para cada escena: selecciónala y pulsa el **botón-miniatura** de la tarjeta (o **«Elegir o cambiar imagen / video…»** a la derecha). Se abre el modal **«Elegir imagen o video para la escena»** con dos pestañas:

**Pestaña «Buscar en bancos»**
1. Escribe la palabra clave (el campo sugiere las 3 primeras palabras del diálogo). **Los términos en inglés dan más resultados.** Pulsa Enter o **«Buscar»**.
2. Opciones de la barra: **«Bancos (n/6) ▾»** (Pexels, Pixabay, NASA, Wikimedia Commons, Openverse —solo imágenes— y Vecteezy), tipo **Videos / Imágenes / Videos e imágenes**, y la casilla **«Solo verticales»** (actívala si el proyecto es vertical).
3. Los resultados salen en una cuadrícula con «Proveedor · duración · ancho×alto / autor». Al pasar el ratón sobre un video, tras 0,5 s se muestra una vista previa. El tooltip trae título, licencia y enlace.
4. **Haz clic en los resultados que quieras** (se pueden marcar varios) y pulsa **«Descargar (n)»**. Si marcaste recursos de **Vecteezy**, la app pregunta si aceptas gastar descargas de la cuota mensual: **responde «No» salvo que el usuario lo haya autorizado.**
5. Al terminar, la app cambia sola a la pestaña **«Desde mi equipo»** con lo descargado seleccionado.

**Pestaña «Desde mi equipo»**
- Muestra todos los archivos del proyecto. Selecciona uno y pulsa **«Usar recurso»** (o doble clic).
- **«Elegir archivo…»** copia imágenes o videos del equipo al proyecto (solo si el usuario te dio ese material).

**Cómo elegir bien** (más detalles en §5): relación visual directa con la frase, sin repetir recursos, orientación acorde al formato, resolución suficiente.

Si un banco falla, el modal muestra «Avisos: …» (por ejemplo `Pexels … HTTP 401 Invalid API key`): usa otro banco; **no edites las claves** y avisa al usuario en el informe.

#### Paso 4 — (Opcional) Ajustes de cada escena
Ver §4.5. Si el usuario no pidió nada específico, **deja los valores por defecto**; sí conviene variar el movimiento de las imágenes entre escenas consecutivas.

#### Paso 5 — Comprobar con vistas previas
- Marca la casilla «Vista previa» de las tarjetas que quieras (deben ser **consecutivas**, si no la app avisa) o deja la escena actual, y pulsa **«▶ Vista previa de la escena»**. La primera vez sintetiza las voces (tarda). Si existe una idéntica, la toma de caché; **«↻ Volver a renderizar»** fuerza una nueva. **«Abrir en Windows»** la abre en el reproductor predeterminado.
- Comprueba: que el recurso corresponde al diálogo, que el movimiento no corte lo importante, que el texto en imagen (si lo hay) se lea y que no haya mensajes de error en el log.
- **La vista previa no es el render final** y no cambia ningún ajuste general.

#### Paso 6 — Dejar todo listo y detenerte
1. Espera 1–2 s tras tu último cambio (autoguardado) y confirma que el panel de mensajes no muestra errores.
2. **No pulses «Renderizar video».** El usuario lo hará.
3. Entrega el informe (§9).

### 4.3 Dónde queda lo que haces

```
data/projects/<nombre>-<4hex>/
├── project.json     # escenas y ajustes del proyecto
├── creditos.txt     # créditos de los recursos de bancos (se actualiza al guardar)
├── assets/          # imágenes y videos descargados o copiados
└── render/preview/cache/   # vistas previas (no es el video final)
```
El video final (`render/<carpeta-del-proyecto>-render.mp4`, por ejemplo `megalodon-gigante-64ca-render.mp4`) lo genera el usuario al renderizar.

### 4.4 Qué NO debes hacer en la ventana (resumen)

- No cambiar nada de las pestañas **Proyecto / Voz / Música / Subtítulos**, ni «Datos para YouTube…».
- No usar «Nuevo proyecto…», «Elegir outro…», «Elegir archivo…» de música, «Probar voz» con cambios, ni los deslizadores de voz/música.
- No pulsar **«Renderizar video»**, «Abrir video renderizado» ni «Abrir carpeta del video».

### 4.5 Opciones de cada escena (panel derecho)

Todas son opcionales y afectan **solo a la escena seleccionada**.

**Pestaña «Imagen / video»**
- **Encuadre:** «Llenar el cuadro» (recorta para llenar), «4:3 sobre fondo difuminado», «Completo sobre fondo difuminado».
- **Movimiento (imágenes):** Imagen fija · Zoom suave de acercamiento / alejamiento · Paneo de abajo hacia arriba / de arriba hacia abajo / de derecha a izquierda / de izquierda a derecha · Zoom lateral hacia la izquierda / derecha. **Intensidad:** «—» (sin movimiento), Sutil, Moderado, Amplio.
- **Inicio del video (clips):** segundo del clip desde el que empieza.

**Pestaña «Texto»**
- «Mostrar subtítulos en esta escena» y su **posición** (Abajo / Centro / Arriba). *(El estilo de los subtítulos —fuente, tamaño, colores— es un ajuste general y no se toca. En proyectos horizontales esta casilla nace apagada: déjala como está salvo petición del usuario.)*
- **«Texto en imagen»:** texto superpuesto (útil para cifras o títulos), con posición, tamaño (24–180 px) y color.

**Pestaña «Audio»**
- «Silenciar la música de fondo en esta escena» y **fades de la música** en la escena (Fade-in / Fade-out, duración 1,5 s por defecto). *(Activar o desactivar la música del proyecto, su volumen y su archivo son ajustes generales.)*
- **Volumen del audio del clip de video:** 0–200 %. 0 % = silencio (valor por defecto). Solo actúa en escenas con video que tengan pista de audio.
- **Efectos de sonido:** se elige uno de la biblioteca (desplegable + «Agregar») o se importa un archivo con «Archivo propio…». Por efecto: «En el segundo» de la escena, volumen, «▶ Escuchar / ⏹ Detener», «Quitar»; y los Fade-in / Fade-out de los efectos de la escena. Un efecto cuyo segundo cae fuera de la escena o cuyo archivo falta se omite y el render lo avisa.

---

## 5. Cómo buscar buenos recursos (cualquier ruta)

- **Palabras clave:** sustantivos concretos en inglés («jaguar jungle», «coral reef aerial», «volcano eruption night»). Si no hay resultados, generaliza («big cat»).
- **Orden de prueba sugerido:** Pexels y Pixabay (video e imagen), luego Wikimedia Commons (especies, historia), NASA (espacio, Tierra) y Openverse (imágenes con licencia abierta). Vecteezy gasta cuota: solo con permiso.
- **Orientación:** en un proyecto vertical prefiere clips/imágenes verticales (o activa «Solo verticales»); en uno horizontal, apaisados. Si usas un recurso de otra orientación, el encuadre «sobre fondo difuminado» evita recortes grandes.
- **Duración del clip:** un video más corto que la escena se repite en bucle; uno más largo se corta (puedes mover el «Inicio del video»).
- **Variedad:** mezcla clips y fotos; alterna planos (general, detalle); no repitas el mismo recurso en dos escenas.
- **Mira antes de elegir:** en la ruta por código, descarga las miniaturas (`preview_url`) de los primeros 6–8 resultados y compáralas (por ejemplo, en una hoja de contactos con FFmpeg `xstack`); así evitas recursos que no tienen que ver con el tema aunque su título lo parezca.
- **Temas muy específicos:** si no hay videos del tema exacto (p. ej. un animal extinto), usa **imágenes** (fósiles, ilustraciones, reconstrucciones de museo) y reserva los videos para escenas de contexto (un tiburón actual, el océano, hielo). Sin inventar: la imagen debe ser lo que dice el diálogo, o una comparación evidente.
- **Calidad:** evita resoluciones muy bajas (< 720 px de ancho), marcas de agua, logos y rostros reconocibles salvo que la licencia lo permita.
- **Licencias:** todo lo descargado de bancos queda en `creditos.txt` con autor, enlace y licencia. Recuérdale al usuario que revise los términos vigentes de cada banco antes de publicar. Los archivos que aporta el usuario («Archivo propio») no salen en créditos.
- **No descargues de sitios fuera de los bancos de la app.**

---

## 6. Ruta B — Operar por código (solo escenas)

Reglas de oro:

1. **Solo modificas `project["scenes"]`.** Nunca cambies `orientation`, `channel`, `voice`, `voice_settings`, `music`, `outro`, `outro_file`, `subtitles`, `youtube` ni `name`.
2. **No uses `create_project()`** (el proyecto ya existe) **ni `render_project()` sin `only_scenes`** (el render final es del usuario).
3. Carga con `load_project`, modifica las escenas y guarda con `save_project`. `save_project` solo reescribe `project.json` y `creditos.txt`: no toca los ajustes recordados por canal.
4. Usa la Ruta B solo con ese proyecto **cerrado** en la ventana (ver aviso de §2).

Ejecuta los scripts **desde la raíz del repo** con el Python del entorno virtual:

```bash
video_factory/.venv/Scripts/python.exe mi_script.py
```

### 6.1 Ejemplo completo y verificado

Añade escenas a un proyecto existente, busca y descarga un recurso para cada una, comprueba que los ajustes generales no cambiaron y hace una vista previa. Se ejecutó de principio a fin.

```python
from pathlib import Path

from video_factory.clips import download_media
from video_factory.pipeline import _find_ffmpeg
from video_factory.project import (
    PROJECTS_DIR, load_project, make_thumbnail, new_scene, register_asset, render_project, save_project,
)
from video_factory.stock_sources import search_media

folder = PROJECTS_DIR / "mi-video-1a2b"                    # carpeta que indicó el usuario (data/projects/<nombre>-<4hex>)
project = load_project(folder)
general_before = {key: value for key, value in project.items() if key not in ("scenes", "updated_at")}
orientation = project.get("orientation", "portrait")        # solo lectura: decide la orientación de los recursos
ffmpeg = _find_ffmpeg()


def attach(scene: dict, query: str, kind: str, providers=("Pixabay", "NASA", "Wikimedia Commons")) -> None:
    """Search, download the best result and set it as the scene's media (same data the GUI stores)."""
    results = search_media(query, providers, kind, vertical_only=orientation == "portrait")
    for warning in results[0].get("search_warnings", []):
        print("AVISO de banco:", warning)
    clip = results[0]                                       # elige con criterio, ver notas
    path = download_media(clip, folder / "assets")
    thumb = make_thumbnail(ffmpeg, path, path.with_suffix(".thumb.jpg"))
    media = {
        "path": path.relative_to(folder).as_posix(), "type": clip.get("media_type", "video"), "provider": clip["provider"], "author": clip["author"],
        "page_url": clip.get("page_url", ""), "license": clip.get("license", ""), "license_url": clip.get("license_url", ""), "title": clip.get("title", ""),
        "attribution": clip.get("attribution", ""), "thumb": thumb.relative_to(folder).as_posix() if thumb.is_file() else None,
    }
    register_asset(folder, media)
    scene["media"] = media


new_scenes = [
    new_scene("El jaguar es el felino más grande de América.", orientation),
    new_scene("Su mordida es una de las más fuertes del reino animal.", orientation),
]
attach(new_scenes[0], "jaguar", "image")
attach(new_scenes[1], "jaguar", "video")
new_scenes[0]["motion"] = "zoom_in"

only_empty = len(project["scenes"]) == 1 and not project["scenes"][0]["dialogue"].strip() and not project["scenes"][0]["media"]
project["scenes"] = new_scenes if only_empty else project["scenes"] + new_scenes     # nunca borres escenas con contenido
save_project(folder, project)

after = {key: value for key, value in load_project(folder).items() if key not in ("scenes", "updated_at")}
assert after == general_before, "¡Se alteraron ajustes generales!"                    # nada general debe cambiar

first = len(project["scenes"]) - len(new_scenes)
preview = render_project(folder, only_scenes=list(range(first, len(project["scenes"]))))   # vista previa (baja resolución), NO el render final
print("Vista previa:", preview["output"])
```

Notas:

- `new_scene(dialogo, orientacion)` crea una escena con los valores por defecto (en horizontal los subtítulos de la escena nacen apagados, igual que en la ventana).
- `search_media(query, providers, media, vertical_only)` — `media` es `"video"`, `"image"` o `"both"`. Lanza `RuntimeError` si no hay resultados (con los avisos de los bancos) y `ValueError` si ningún banco elegido ofrece ese tipo. Nombres de banco válidos: `Pexels`, `Pixabay`, `NASA`, `Wikimedia Commons`, `Openverse` (solo imágenes), `Vecteezy` (consume cuota; no lo uses sin permiso).
- **Elegir resultados:** no te quedes ciegamente con `results[0]`. Revisa `title`, `width`×`height`, `duration` (para video, ≥ la duración estimada de la escena o acepta el bucle) y la orientación. Si puedes ver la miniatura (`preview_url`) o el archivo descargado, valida que corresponde al tema.
- Un banco puede devolver error (clave inválida, cuota) sin que la búsqueda falle: míralo en `search_warnings` y repórtalo.
- `render_project(folder, only_scenes=[...])` genera una **vista previa** en `render/preview/cache/` (primera vez sintetiza voces). Sin `only_scenes` sería el render final: **no lo hagas**.
- Para **ensayar sin tocar nada del usuario**, trabaja sobre una copia del proyecto en una carpeta temporal **de ruta corta** (por ejemplo `C:\vf_test`): las rutas de Windows de más de 260 caracteres pueden hacer fallar las vistas previas.

### 6.2 Ajustes de escena por código

```python
scene = project["scenes"][0]
scene.update({"chapter": "Introducción", "motion": "pan_right", "zoom": {"speed": "medium", "direction": "in"},
              "crop": "fill_9_16", "extra_seconds": 0.5, "show_subtitles": True, "subtitle_pos": "bottom"})
scene["text_overlay"] = {"text": "13 METROS", "position": "top", "size": 64, "color": "#FFFFFF"}
scene["sfx"] = [{"path": "shared:sfx_library/whoosh.wav", "at": 1.0, "gain": 0.8}]
scene["music_fade"] = {"in": True, "out": False, "seconds": 1.5}
save_project(folder, project)
```

### 6.3 Otras funciones útiles de `video_factory.project`

| Función | Para qué |
|---|---|
| `split_script(texto)` | Parte un guion en párrafos (separados por línea en blanco) |
| `estimate_seconds(dialogo, fallback, extra)` | Estima la duración de una escena |
| `import_media(folder, Path(archivo))` | Copia un archivo del usuario a `assets/` y devuelve su ruta relativa (arma el `media` con `"provider": "Archivo propio"`) |
| `list_assets(folder)` | Lista los recursos ya presentes en el proyecto |
| `list_sfx_library(ffmpeg)` | `[(nombre, referencia)]` de la biblioteca de efectos |

---

## 7. Referencia de la escena (lo que sí puedes escribir)

| Campo | Valores / significado |
|---|---|
| `dialogue` | Texto que se narra. Vacío = escena muda de `duration` segundos |
| `chapter` | Título de capítulo para YouTube (solo si el usuario lo pidió) |
| `media` | `{"path", "type": "image"\|"video", "provider", "author", "page_url", "license", "license_url", "title", "attribution", "thumb"}` — **obligatorio**: sin recurso el usuario no podrá renderizar |
| `crop` | `"fill_9_16"` (llena el cuadro) \| `"4_3_blur"` \| `"fit_blur"` |
| `motion` | `none`, `zoom_in`, `zoom_out`, `pan_up`, `pan_down`, `pan_left`, `pan_right`, `zoom_left`, `zoom_right` (solo imágenes) |
| `zoom` | `{"speed": "none"\|"slow"\|"medium"\|"fast", "direction": "in"\|"out"}` — `speed` es la intensidad; con `"none"` la imagen queda fija |
| `start` | Segundo inicial del clip (videos) |
| `duration` | Duración base si no hay diálogo (3,0 s por defecto) |
| `extra_seconds` | Segundos extra tras la narración |
| `show_subtitles`, `subtitle_pos` | `bool`; `"bottom"`\|`"middle"`\|`"top"` |
| `text_overlay` | `{"text", "position": "top"\|"middle"\|"bottom", "size": 24–180, "color": "#RRGGBB"}` |
| `mute_music` | `bool` — silencia la música durante la escena |
| `music_fade` | `{"in": bool, "out": bool, "seconds": 1.5}` |
| `clip_volume` | 0.0–2.0 — volumen del audio del clip de video (0 = silenciado) |
| `sfx` | `[{"path": "shared:sfx_library/…", "at": segundos desde el inicio de la escena, "gain": 0.05–2.0}]` |
| `sfx_fade` | `{"in": bool, "out": bool, "seconds": 1.5}` |

Los campos que falten se completan solos con sus valores por defecto al cargar el proyecto.

**Biblioteca de efectos** (`shared:sfx_library/…`): trae 9 efectos sintéticos (Whoosh, Subida, Bajada, Pop, Ding, Golpe grave, Tic, Alerta, Suspenso); cualquier audio colocado en `data/sfx_library/` aparece en el desplegable.

**Ajustes generales (solo lectura para ti):** `orientation` (`portrait` 1080×1920 / `landscape` 1920×1080), `channel` (`que-curioso` / `belleza`), `voice` (`male`, `male_neutral`, `male_mx`, `female`, `female_neutral`, `female_co`), `voice_settings`, `music`, `outro`, `subtitles`, `youtube`. Léelos para decidir, no los modifiques.

---

## 8. Solución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| «No encuentro FFmpeg» | FFmpeg no está en el PATH ni en la carpeta de winget | Avisar al usuario (instalar con `winget install Gyan.FFmpeg`) |
| «Falta edge-tts en …\data\tts-packages» | No se instaló edge-tts | Avisar al usuario (`instalar.bat`); sin voz no hay vista previa con diálogo |
| Error al sintetizar la voz en la vista previa | Sin internet o servicio de voz no disponible | Reintentar; si persiste, informar |
| «Avisos: Pexels … HTTP 401» en la búsqueda | Clave de ese banco inválida o vencida | Usar otros bancos; avisar al usuario (no edites `.env`) |
| «No se encontraron resultados» | Palabra clave demasiado específica o solo en español | Probar en inglés y términos más generales |
| «Selección no consecutiva» al pedir vista previa | Casillas de «Vista previa» con huecos | Marcar solo escenas contiguas |
| «Escena N: se omitió el efecto …» | Archivo del efecto ausente o segundo fuera de la escena | Corregir `at` o quitar el efecto |
| «Escena N: el clip de video no tiene audio» | Volumen de clip > 0 en un clip sin audio | Dejarlo en 0 |
| La vista previa falla sin motivo aparente | Ruta del proyecto demasiado larga (> 260 caracteres) | Informar al usuario; probar en una carpeta con ruta corta |
| Tus escenas desaparecieron tras editar el JSON | La ventana tenía el proyecto abierto y lo sobrescribió | Cerrar la ventana y repetir (o usar la Ruta A) |

---

## 9. Reglas de conducta

1. **Alcance:** solo escenas. Los ajustes generales y el render final son del usuario (§0). Ante la duda, pregunta o avisa; no cambies.
2. **No toques proyectos ajenos** ni borres escenas con contenido, recursos ni archivos del usuario.
3. **Nunca expongas secretos.** `video_factory\.env` contiene claves reales: no las muestres ni las incluyas en informes.
4. **Pide confirmación** antes de gastar descargas de Vecteezy, usar material del usuario fuera del proyecto o hacer cualquier cosa que no sea preparar escenas.
5. **No hagas `git commit`/`push`** de datos de proyectos: `data/` no se versiona a propósito.
6. **Licencias:** avisa de que `creditos.txt` debe revisarse antes de publicar.
7. **Informa con honestidad:** distingue lo que verificaste de lo que no.

---

## 10. Lista de verificación final («listo para renderizar»)

- [ ] Trabajaste en el proyecto que indicó el usuario y **no cambiaste ningún ajuste general** (formato, canal, voz, música, outro, subtítulos, datos de YouTube).
- [ ] El guion está en español latinoamericano, sin datos sin verificar, repartido en escenas de 1–2 frases.
- [ ] **Todas** tus escenas tienen recurso visual relacionado con su diálogo y sin repeticiones.
- [ ] Hiciste vista previa de las escenas con movimiento, texto en imagen o efectos y no hubo errores en el log.
- [ ] El proyecto quedó guardado (autoguardado de la ventana, o `save_project` en la Ruta B).
- [ ] **No renderizaste el video final.**

### Informe final sugerido

```text
Proyecto: <nombre> (formato: <vertical/horizontal>, canal: <canal> — solo lectura)
Escenas creadas: <n> (de la <k> a la <m>) · Duración estimada: ~<s> s
- Escena 1: "<resumen del diálogo>" → <proveedor> <imagen/video> "<título>"
- Escena 2: …
Ajustes de escena aplicados: <lista, o "valores por defecto">
Avisos: <bancos con error, recursos de baja resolución, efectos omitidos, etc. — o "ninguno">
Sugerencias sobre ajustes generales (no los cambié): <p. ej. "la voz podría ser más lenta">, o "ninguna"
Créditos: data\projects\<proyecto>\creditos.txt (revisar términos antes de publicar)
Listo: ya puedes pulsar «Renderizar video».
```
