# Video Factory — Documento de contexto para continuar el desarrollo

> Estado documentado: cambios locales de formato horizontal, render largo y metadatos para YouTube sobre el commit `db0a8b0` de `main`, 26 de octubre de 2026. Los cambios aún no están committeados ni se verificó el render con FFmpeg.
> Este documento describe **lo que existe en el código hoy**, por qué está hecho así, qué trampas se encontraron y cómo extenderlo sin romper lo existente. Antes de basarte en un dato concreto (firma, ruta, nombre), verifica en el archivo: el usuario a veces restaura o edita archivos por su cuenta.

---

## 1. Qué es el proyecto

**Video Factory** es una aplicación de escritorio para **Windows** (Python + PySide6) que produce **videos cortos verticales 9:16** (Reels, TikTok, Shorts) a partir de un **guion libre dividido en escenas**:

- Cada escena tiene un **diálogo** (se convierte en voz neuronal con Microsoft Edge TTS) y **un recurso visual** (imagen o video) que puede venir de bancos gratuitos (Pexels, Pixabay, NASA, Wikimedia Commons, Openverse, Vecteezy) o de archivos del usuario.
- La **duración de cada escena narrada** es la duración de su voz más una pausa de 0.35 s y el campo opcional `extra_seconds` (segundos adicionales de imagen/silencio, editable en cada tarjeta). En escenas sin diálogo se suma `extra_seconds` a `duration` (o a los 3 s por defecto). La duración total del video es la suma; el objetivo de 45 s es solo un indicador/aviso.
- El render usa **FFmpeg** (encuadre 9:16, zoom suave en imágenes, subtítulos ASS quemados, música de fondo con fade-out, outro opcional).
- Hay **dos canales** (plantillas de marca): "Qué curioso…¿no?" y "Belleza con evidencia"; cada uno recuerda su última configuración (voz, subtítulos, música, outro).
- La app genera automáticamente un archivo de **créditos** (`creditos.txt`) con autor, enlace y licencia de cada recurso de banco usado.

El usuario es **Adrian (Genxapp)**, desarrollador; trabaja en español latinoamericano. El proyecto nació de un ZIP de un proyecto Python previo (pipeline basado en catálogo) y de una primera GUI creada con ChatGPT; ese código **original se conserva** pero la aplicación actual ya no lo usa (salvo constantes y utilidades, ver §4).

---

## 2. Reglas de colaboración con el usuario (importante)

Estas reglas vienen de las preferencias globales de Adrian y de lo observado en la sesión:

1. **Responder siempre en español latinoamericano.** Respuestas concisas: primero el resultado, sin narrar pasos.
2. **Código, docstrings y comentarios en inglés; textos que ve el usuario (UI, avisos, errores mostrados) en español.** Nombres de campos existentes en español se quedan.
3. **Pocos comentarios `#`**: docstrings sí; comentarios solo para el "por qué" no obvio. El estilo real del repo: líneas largas, f-strings densas, pocas abstracciones (no hay Black aplicado en este repo).
4. **Cambios pequeños y verificados.** Probar de verdad (ejecutar, capturar pantalla, medir) antes de afirmar que algo funciona; distinguir lo probado de lo no probado y decirlo.
5. **Commits solo cuando el usuario lo pide** ("haz el commit y el push"). Mensajes en inglés, imperativo, con cuerpo explicativo y la línea final `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. En esta sesión el usuario pidió explícitamente tanto el commit como el push cada vez; si no lo pide, no subir.
6. **No tocar ni mostrar secretos**: `video_factory/.env` contiene claves reales (Pexels, Pixabay, Vecteezy). Nunca imprimirlas; para verificar solo mostrar longitud/prefijo o "tiene valor".
7. **Antes de borrar o sobrescribir datos del usuario, mirar el contenido.** En pruebas usar carpetas temporales (scratchpad) y **parchear `project.DEFAULTS_FILE`** para no tocar `data/channel_defaults.json` real.
8. No hacer refactors amplios ni renombrar campos de `project.json` sin migración (hay proyectos reales del usuario en `data/projects/`).
9. Archivos sin seguimiento que no creaste (p. ej. `Canal/Celebración de 300 suscriptores.png`) **no se incluyen en commits**.
10. Los módulos originales del proyecto (`pipeline.py`, `catalog.py`, `storage.py`, `cli.py`, etc.) **no se modifican** salvo necesidad justificada (hoy solo se importan constantes/utilidades de `pipeline.py` y `storage.py`).

---

## 3. Entorno, instalación y despliegue

- **SO objetivo:** Windows 10/11 (se usa `os.startfile`, `explorer /select`, `taskkill`, `ctypes.windll`, accesos directos `.lnk`). No hay soporte para otros SO.
- **Python:** el entorno del usuario usa 3.14 (venv en `video_factory/.venv/`); el instalador acepta 3.11+.
- **Dependencias:** `video_factory/requirements-gui.txt` = `PySide6>=6.7,<7` y `tzdata` (Windows no trae zonas horarias; `storage.now_iso()` usa `ZoneInfo("America/Bogota")`). PySide6 6.12 instalado. `edge-tts` **no** va en el venv: se instala con `pip install --target data/tts-packages edge-tts` y `synthesize_neural_voice.py` añade esa carpeta a `sys.path`.
- **FFmpeg:** debe estar en PATH o instalado con winget (`Gyan.FFmpeg`); `pipeline._find_ffmpeg()` busca en PATH y en `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffmpeg.exe`. FFmpeg 9.0.2 (gyan full build) en el equipo del usuario. Se usa `ffmpeg` (no hay llamadas a `ffprobe` en el flujo actual; la información de medios se obtiene parseando `ffmpeg -i`).
- **`instalar.bat`** (raíz): crea `video_factory/.venv`, instala requisitos, instala `edge-tts` en `data/tts-packages`, instala FFmpeg con winget si falta, crea `video_factory/.env` desde `.env.example` si no existe y crea el acceso directo "Video Factory" en el Escritorio (apunta a `pythonw.exe -m video_factory.gui`, carpeta de trabajo = raíz del proyecto, icono `assets/video_factory.ico`). Acepta `/silencioso` (sin `pause`).
- **Ejecución:** `python -m video_factory.gui` (o el acceso directo, que usa `pythonw` → **sin consola**; por eso hay un `excepthook` que muestra un cuadro de error y escribe `data/logs/error.log`).
- **Claves (`video_factory/.env`, NO versionado):** `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `VECTEEZY_ACCOUNT_ID`, `VECTEEZY_API_KEY`. Se leen con `clips.load_env_file()` (parser propio; no usa python-dotenv; no pisa variables ya definidas). NASA, Wikimedia Commons y Openverse no requieren clave.
- **Dos `APP_ROOT` distintos (trampa):** `clips.APP_ROOT` = carpeta `video_factory/` (de ahí sale `video_factory/.env`); `storage.APP_ROOT` / `pipeline.APP_ROOT` = raíz del repo (de ahí salen `Canal/`, `data/`, `assets/`). No confundirlos.
- **Repositorio:** `https://github.com/AdrianSilvaTj/video_factory.git`, rama `main`. El usuario también sube archivos por la web de GitHub (el commit `bc978e8` "Add files via upload" trajo `Canal/*`), por lo que antes de empujar puede hacer falta `git pull --rebase origin main` (con `git stash` si hay cambios sin commit).
- **Archivos de canal en el repo:** `Canal/fondo_1.mp3`, `Canal/outro_sincronizado.mp4`, `Canal/belleza_fondo.mp3` (versionados; el usuario los subió; avisar que deben tener derechos de uso).
- **`.gitignore`:** `.env`, `*.env` (salvo `.env.example`), `__pycache__/`, `*.pyc`, `.venv/`, `data/`, `revision/`, `*.lnk`.
- **Otro PC (Windows 11):** el usuario instaló desde el repo con `instalar.bat`; el usuario reportó que la ventana pedía el nombre del proyecto y no terminaba de abrir; el diagnóstico (no confirmado por el usuario) fue `tzdata` ausente, porque `create_project` llama a `now_iso()`; se añadió `tzdata` a los requisitos y el `excepthook`. Si algo falla ahí, revisar `data/logs/error.log` o ejecutar con `video_factory\.venv\Scripts\python.exe -m video_factory.gui` para ver la traza.

---

## 4. Estructura del repositorio (qué está vivo y qué es heredado)

```
video_factory_gui_mvp/
├── instalar.bat                 # instalador para otro PC (VIVO)
├── README.md                    # guía corta (VIVO)
├── requerimientos.md            # documento de traspaso original (ChatGPT): histórico
├── README_ETAPA2.md             # obsoleto (describía las pestañas antiguas)
├── assets/
│   ├── make_icon.py             # genera video_factory.ico/.png con QPainter (VIVO)
│   ├── video_factory.ico        # 7 tamaños 16-256 px, PNG dentro del ICO
│   └── video_factory.png
├── Canal/                       # música y outro de los canales (versionados)
│   ├── LEEME.txt  fondo_1.mp3  outro_sincronizado.mp4  belleza_fondo.mp3
├── docs/CONTEXTO_PARA_IA.md     # este documento
├── data/                        # NO versionado: datos del usuario (ver §5)
└── video_factory/
    ├── gui/
    │   ├── __main__.py          # entrada: from .studio import main
    │   ├── studio.py            # ventana única StudioWindow + SceneCard (VIVO, ~960 líneas)
    │   ├── media_dialog.py      # modal de recursos MediaDialog (VIVO)
    │   ├── frame_preview.py     # vista previa estática del cuadro (VIVO)
    │   └── workers.py           # run_task: hilos de trabajo (VIVO)
    ├── project.py               # modelo de proyecto + render + créditos + defaults (VIVO, núcleo)
    ├── channels.py              # VOICES, CHANNELS, TARGET_SECONDS, _AUDIO_FMT (VIVO)
    ├── stock_sources.py         # bancos: NASA, Wikimedia, Openverse, Vecteezy + search_media (VIVO)
    ├── clips.py                 # Pexels/Pixabay, descarga, constantes de extensiones (VIVO parcial)
    ├── proc.py                  # run() sin consola y cancelable (VIVO)
    ├── synthesize_neural_voice.py  # script externo edge-tts → mp3 → wav (VIVO)
    ├── requirements-gui.txt  .env.example
    ├── pipeline.py  storage.py  # ORIGINALES: solo se importan constantes/utilidades (ver abajo)
    ├── catalog.py cli.py compose_3d_infographics.py infographic_prompts.py
    │   redesign_openers.py split_contact_sheet.py synthesize_voice.ps1 estilo_infografia_3d.md
    │   plantilla_infografia.png requirements-stage2.txt README_GUI.md   # HEREDADOS, sin uso en la GUI
```

**Qué se usa de los módulos originales:**
- `pipeline.py`: `APP_ROOT`, `BACKGROUND_MUSIC` (`Canal/fondo_1.mp3`), `BACKGROUND_MUSIC_GAIN` (0.30), `SYNCHRONIZED_OUTRO` (`Canal/outro_sincronizado.mp4`), `EDGE_TTS_PACKAGES` (`data/tts-packages`), `_find_ffmpeg()`.
- `storage.py`: `APP_ROOT`, `load_json`, `save_json` (escritura atómica con `.tmp` + `os.replace`), `now_iso()` (zona Bogotá), `slug()`.
- `clips.py` conserva funciones de la "etapa 2" sin uso en la GUI actual: `search_clips`, `download_approved_clips`, `add_local_files`, `_load_manifest`, `TARGET_SECONDS`. Se mantienen por compatibilidad; las funciones **vivas** de `clips.py` son: `load_env_file`, `_request_json`, `_safe_name`, `_rank`, `search_pexels`, `search_pixabay`, `search_pexels_images`, `search_pixabay_images`, `_download_file`, `download_media`, `IMAGE_EXTENSIONS`, `VIDEO_EXTENSIONS`.
- `catalog.py` (diccionario `IDEAS` de guiones por tema) **ya no interviene**: la app dejó de depender del catálogo (guion libre).

---

## 5. Datos en disco (formatos exactos)

Todo lo del usuario vive en `data/` (no versionado). `data/` = `PROJECTS_DIR.parent` = `<raíz>/data`.

```
data/
├── projects/<slug>-<4hex>/            # un proyecto (slug del nombre + sufijo aleatorio)
│   ├── project.json                   # estado del proyecto (esquema abajo)
│   ├── creditos.txt                   # se reescribe en cada save_project()
│   ├── assets/                        # recursos del proyecto
│   │   ├── <archivo>.mp4|.jpg|…       # descargados (nombre = id del recurso) o copiados (prefijo uuid6_slug)
│   │   ├── <archivo>.thumb.jpg        # miniatura 640 px de ancho
│   │   └── library.json               # {ruta_relativa: media_dict} de lo descargado de bancos
│   ├── voice/<hash16>.wav|.mp3        # caché de voz sintetizada
│   └── render/
│       ├── video.mp4  render.json  creditos.txt  captions.ass
│       ├── .work-<id>/scenes/scene-NNNN.mp4|.wav|-frame.png # intermedios temporales de render; se borran al completar
│       ├── frames/<stem>_<seg>.jpg    # fotogramas de videos para la vista previa de "Inicio"
│       └── preview/scene.mp4 + captions.ass   # vista previa de UNA escena (540x960 o 960x540)
├── channel_defaults.json              # {"last_channel": clave, "channels": {clave: ajustes}}
├── channel_defaults/<canal>/<archivo> # música/outro COMPARTIDOS por canal (una sola copia)
├── search_history.json                # lista de ≤20 términos, el más reciente primero
├── tts-packages/                      # edge-tts instalado con pip --target
├── logs/error.log                     # excepciones no capturadas (excepthook)
└── jobs/ …                            # restos del flujo antiguo basado en catálogo: ignorar
```

### 5.1 `project.json`
```json
{
  "schema_version": 1,
  "name": "Mi video",
  "channel": "que-curioso",                  // clave de CHANNELS
  "orientation": "portrait",                 // portrait (9:16) | landscape (16:9)
  "voice": "male",                           // clave de VOICES
  "voice_settings": {"rate": -4, "pitch": -1, "volume": 0},   // enteros: % , Hz , %
  "music": {"enabled": true, "gain": 0.3, "path": null, "name": null},
  "outro": true,                             // bool: incluir outro
  "outro_file": null, "outro_name": null,    // outro propio (referencia 'shared:...')
  "subtitles": {"font": "Arial", "size": 128, "color": "#FFFFFF", "outline": "#241B10", "bold": true},
  "youtube": {"title": "Mi video", "description": "", "tags": []},
  "scenes": [ { …escena… } ],
  "created_at": "…", "updated_at": "…"
}
```
- `music.path`: `null` = usar la música del canal (`CHANNELS[canal]["music"]`); `"shared:channel_defaults/<canal>/<archivo>"` = archivo compartido; una ruta sin prefijo = relativa a la carpeta del proyecto (proyectos antiguos). Se resuelve SIEMPRE con `project.resolve_asset(folder, ref)`.
- `outro_file`: igual; `null` = usar `CHANNELS[canal]["outro"]` (puede ser `None`, p. ej. Belleza).
- `load_project()` aplica **migraciones perezosas** con `setdefault` (`voice_settings`, `outro_file`, `outro_name`, `subtitles`, `orientation=portrait`, `youtube`, `music.path`) y migra escenas antiguas de `zoom.direction` a `motion`. **Cualquier campo nuevo debe añadirse aquí con `setdefault`** para no romper proyectos viejos.

### 5.2 Escena (`new_scene()`)
```json
{
  "id": "a1b2c3d4", "dialogue": "texto…", "chapter": "Título opcional de YouTube",
  "motion": "zoom_in",               // preset de movimiento de imagen; proyectos viejos se migran desde zoom
  "media": null | {media_dict},
  "crop": "fill_9_16" | "4_3_blur" | "fit_blur",
  "zoom": {"speed": "none|slow|medium|fast", "direction": "in|out"},   // valores históricos para migración
  "start": 0.0,                 // segundo de inicio del clip (solo videos)
  "duration": 3.0,              // duración base si el diálogo está vacío
  "extra_seconds": 0.0,         // segundos adicionales al final de esta escena
  "text_overlay": {"text": "", "position": "top", "size": 64, "color": "#FFFFFF"}, // texto opcional sobre la imagen
  "subtitle_pos": "bottom" | "middle" | "top",
  "show_subtitles": true
}
```
Para campos de escena nuevos: leerlos siempre con `scene.get("campo", valor_por_defecto)` (hay escenas guardadas sin ellos).

### 5.3 `media_dict` (recurso asignado a una escena)
```json
{"path": "assets/pixabay-223551.mp4", "type": "video|image", "provider": "Pixabay",
 "author": "…", "page_url": "…", "license": "…", "license_url": "…", "title": "…",
 "attribution": "…", "thumb": "assets/pixabay-223551.thumb.jpg" | null}
```
- `provider == "Archivo propio"` (autor "Aportado por el usuario") marca archivos del usuario: **no** aparecen en `creditos.txt`.
- `path` y `thumb` son relativos a la carpeta del proyecto.

### 5.4 Resultado de búsqueda (dict de `stock_sources`, antes de descargar)
Campos: `id` (`<proveedor>-<[img-]><id>`), `provider`, `provider_id`, `media_type` (`video|image`), `query`, `title`, `duration`, `width`, `height` (0 si el banco no las informa), `download_url` (puede ser `""` y resolverse al descargar, ver Vecteezy), `fallback_urls` (opcional), `page_url`, `author`, `author_url`, `attribution`, `license`, `license_url`, `preview_url` (miniatura), `preview_video_url` (mp4 corto para la vista previa al pasar el mouse, puede ser `""`), `search_warnings` (lista de avisos de bancos que fallaron; la pone `search_media`).

### 5.5 `channel_defaults.json`
```json
{"last_channel": "belleza",
 "channels": {"belleza": {"voice": "female_neutral", "voice_settings": {…}, "outro": true,
   "subtitles": {…}, "outro_file": "shared:channel_defaults/belleza/x.mp4"|null, "outro_name": "…"|null,
   "music": {"enabled": true, "gain": 0.55, "name": "mi.mp3", "file": "shared:channel_defaults/belleza/mi.mp3"|null}}}}
```

---

## 6. Módulos: responsabilidades, API y detalles

### 6.1 `channels.py`
- `VOICES`: claves `male` (es-CO-GonzaloNeural, rate -4%, pitch -1Hz), `male_neutral` (es-US-AlonsoNeural), `male_mx` (es-MX-JorgeNeural), `female` (es-MX-DaliaNeural, +9%, +4Hz — la voz del Canal Belleza), `female_neutral` (es-US-PalomaNeural), `female_co` (es-CO-SalomeNeural). Cada una: `label`, `voice` (nombre Edge), `rate`, `pitch` (cadenas como `"+9%"`, `"+4Hz"`), `gender`. Las voces existen realmente en Edge TTS (verificado con `edge_tts.list_voices()`).
- `CHANNELS`: `que-curioso` (música `Canal/fondo_1.mp3` al 0.30, outro `Canal/outro_sincronizado.mp4`, subtítulos Arial 128 blancos con contorno #241B10, voz `male`) y `belleza` (música `Canal/belleza_fondo.mp3` al 0.14, sin outro, subtítulos Segoe UI 76 lavanda #D7B9FF con contorno #361B49, voz `female`). Claves de cada canal: `label`, `music`, `music_gain`, `outro`, `subtitles`, `default_voice`.
- `TARGET_SECONDS = 45`, `_AUDIO_FMT` (cadena de filtros de audio común: 48 kHz, fltp, estéreo).
- **Los tamaños de subtítulo por defecto fueron duplicados a petición del usuario** (antes 64 y 38).

### 6.2 `proc.py` — ejecución de programas externos
- `run(cmd, capture_output=False, timeout=None, **kwargs)`: **reemplazo de `subprocess.run`** (misma forma de retorno: `CompletedProcess`). Añade `creationflags=CREATE_NO_WINDOW` (sin ventanas de consola) y es **cancelable**: usa `Popen` + `communicate(timeout=0.2)` en bucle.
- `cancel_all()` marca un `threading.Event`; el programa en curso se mata con `taskkill /F /T` (árbol de procesos) y se lanza `Cancelled` (mensaje `proc.CANCELLED = "Cancelado por el usuario."`). `reset()` limpia el evento (la GUI lo llama al empezar un proceso).
- **Regla:** todo subprocess de la app debe pasar por `proc.run` (ya lo hacen `project.py`). La única excepción: `studio.py` usa `subprocess.Popen(["explorer", "/select,", ...])` para abrir el Explorador.
- `synthesize_neural_voice.py` (proceso hijo) añade su propio `creationflags` al llamar a FFmpeg.

### 6.3 `project.py` — núcleo
Constantes: `PROJECTS_DIR`, `SCENE_PAUSE = 0.35`, `EMPTY_SCENE_SECONDS = 3.0`, `CROPS` (clave→etiqueta en español), `ZOOM_SPEEDS = {none:0, slow:0.08, medium:0.16, fast:0.28}` (fracción total de acercamiento), `MUSIC_EXTENSIONS`, `OUTRO_EXTENSIONS`, `SUBTITLE_POSITIONS = {bottom:("Default",2), middle:("Middle",5), top:("Top",8)}` (nombre de estilo ASS, alineación), `SHARED_PREFIX = "shared:"`, `DEFAULTS_FILE = data/channel_defaults.json`.

Funciones (todas síncronas, sin Qt; reutilizables desde scripts):
| Función | Qué hace |
|---|---|
| `new_scene(dialogue="")` | Dict de escena con valores por defecto |
| `create_project(name, channel=None, root=None) -> Path` | Crea carpeta `slug-xxxx/` con `assets/`, arma `project.json`, aplica los ajustes guardados del canal (`apply_channel_defaults`) y guarda. `channel=None` → `last_channel()` |
| `load_project(folder)` / `save_project(folder, project)` | Lee con migraciones / escribe `project.json` y **reescribe `creditos.txt`** |
| `write_credits(folder, project)` | Lista recursos de banco usados en escenas (sin duplicados por `path`) con título, enlace, licencia, términos y atribución; escribe `creditos.txt` |
| `import_media(folder, source) -> str` | Copia un archivo a `assets/` con nombre `uuid6_slug.ext`; devuelve ruta relativa |
| `load_library`, `register_asset`, `list_assets(folder)` | `assets/library.json` guarda el `media_dict` de lo descargado; `list_assets` devuelve un `media_dict` por cada imagen/video de `assets/` (excluye `*.thumb.jpg`), más recientes primero; completa con metadatos de `library.json` o de las escenas; si no hay datos, "Archivo propio" |
| `make_thumbnail(ffmpeg, media, target)` | JPEG 640 px (para video, frame en 0.5 s; reintenta en 0) |
| `extract_frame(ffmpeg, media, second, target)` | JPEG 640 px del segundo indicado; `RuntimeError` si no existe ese fotograma |
| `voice_defaults(voice_key)` | `{"rate","pitch","volume"}` enteros del preset |
| `synthesize_voice(folder, text, voice_key, settings, ffmpeg) -> Path` | WAV en caché `voice/<sha256(texto|voz|rate|pitch|volume)[:16]>.wav`; si no existe, ejecuta `synthesize_neural_voice.py` con `proc.run` (timeout 180 s) |
| `estimate_seconds(dialogue, fallback)` | ≈ palabras/2.6 + 0.35 s (solo estimación para la UI) |
| `split_script(text)` | Párrafos separados por línea en blanco → lista de diálogos |
| `wrap_width_for(size)` | `max(8, int(900/(size*0.52)))` caracteres por línea de subtítulo |
| `caption_chunks(text, max_chars)` | Agrupa palabras en bloques ≤ max_chars (el render usa `wrap_width*2`) |
| `subtitle_style_line(sub, name, alignment, margin_v)` | Línea `Style:` ASS (colores `#RRGGBB`→`&H00BBGGRR`, contorno = `max(4, round(size/12))`, MarginV por defecto 420) |
| `render_project(folder, ffmpeg_explicit=None, progress=None, only_scene=None, only_scenes=None, force_preview=False)` | Render completo o vista previa de una escena/bloque consecutivo (ver §7). Las vistas se guardan en caché por huella de escena/ajustes/archivos; `force_preview=True` fuerza una nueva. **Lee el proyecto desde disco** (`load_project`): la GUI debe guardar antes |
| `load_search_history`, `add_search_term(term, limit=20)` | `data/search_history.json` (sin duplicados, insensible a mayúsculas) |
| `import_shared(channel, source) -> "shared:…"` | Copia **una sola vez** música/outro a `data/channel_defaults/<canal>/` (si ya existe un archivo del mismo nombre con distinto tamaño, añade sufijo) y devuelve la referencia |
| `resolve_asset(folder, ref) -> Path` | `shared:` → `data/…`; otro valor → `folder/ref` |
| `remember_channel_defaults(folder, project)` | Guarda voz, ajustes de voz, outro (+archivo), subtítulos y música (+archivo compartido) bajo la clave del canal y fija `last_channel`. Convierte archivos propios del proyecto (formato antiguo) en compartidos |
| `apply_channel_defaults(folder, project) -> bool` | Aplica lo guardado del canal al dict del proyecto; `False` si no hay nada (el llamador usa los presets de `CHANNELS`) |
| `last_channel()` | Último canal usado (o `que-curioso`) |

### 6.4 `clips.py` (parte viva)
- `load_env_file()`, `_request_json(url, headers=None)` (User-Agent propio, timeout 30 s, errores HTTP → `RuntimeError("API respondió HTTP …")`), `_safe_name`, `_rank` (prioriza proporción vertical y duración 3-25 s).
- `search_pexels` (endpoint `videos/search`, `orientation=portrait`, elige el archivo con ancho más cercano a 1080; añade `preview_video_url` = archivo más pequeño), `search_pixabay` (`api/videos`, variante `medium`, `preview_video_url` = `tiny`), `search_pexels_images` (`/v1/search`, `orientation=portrait`), `search_pixabay_images` (`image_type=photo`).
- `_download_file(url, path)`: solo `https`; User-Agent propio; reintenta **3 veces con espera** ante HTTP 429; borra el parcial si falla; tope de seguridad 500 MB.
- `download_media(item, destination) -> Path`: si el proveedor es Vecteezy y `download_url` está vacío, llama a `stock_sources.resolve_vecteezy_download` (gasta una descarga de cuota); prueba `download_url` y luego `fallback_urls` (convierte `http://` en `https://`); la extensión sale de la URL si es conocida, si no `.jpg` (imagen) o `.mp4`. Si el archivo ya existe lo reutiliza. Es la **única vía de descarga** de la app.

### 6.5 `stock_sources.py` — bancos
- `SOURCES = {banco: (tipos…)}`: Pexels, Pixabay, NASA, Wikimedia Commons, Vecteezy (video e imagen) y Openverse (solo imagen). `_SEARCHERS[(banco, tipo)] = lambda q, vertical_only`.
- `search_media(query, providers, media="video|image|both", vertical_only=False)`: ejecuta **en paralelo** (ThreadPoolExecutor) todas las combinaciones banco×tipo; un banco que falla no impide los demás (el error va a `search_warnings`); aplica `license` por defecto (`"Licencia de <banco>"`); con `vertical_only` filtra `height > width` pero **conserva los de dimensiones desconocidas** (`width == 0`); ordena por `_rank`; lanza `RuntimeError` solo si no hay ningún resultado.
- Peculiaridades por banco (todas verificadas con peticiones reales):
  - **Pexels / Pixabay**: requieren clave. *La clave de Pexels del usuario devuelve HTTP 401 ("Invalid API key"): el usuario no consigue una válida; la app lo tolera y sigue con los demás bancos.*
  - **NASA** (`images-api.nasa.gov`): sin clave, dominio público. No informa dimensiones. URLs por convención `https://images-assets.nasa.gov/{video|image}/{id}/{id}~medium.mp4|~large.jpg` (con `fallback_urls`); preview de video `~preview.mp4`. Licencia con aviso sobre personas/logos.
  - **Wikimedia Commons** (API `action=query`, `generator=search`, `filetype:video|bitmap`): licencia y autor salen de `extmetadata` (se limpia el HTML). Videos: usa transcodificados `…/transcoded/…/<archivo>.720p.vp9.webm` (fallback 480p y original) porque los originales pueden pesar cientos de MB; preview `360p`. Puede responder 429 (de ahí el reintento y el User-Agent propio). Imágenes > 60 MB se omiten.
  - **Openverse** (`api.openverse.org/v1/images`): **anónimo permite `page_size` ≤ 20**; licencias Creative Commons (se guardan como `CC BY-SA 2.0`, etc.); solo URLs `https`.
  - **Vecteezy** (`api.vecteezy.com/v2/{account_id}/resources`, `Authorization: Bearer`): plan gratuito = **500 descargas/mes** (la búsqueda gasta cuota *general*, la descarga cuota de *descargas*). La URL de descarga firmada (24 h) se pide **solo al descargar** (`resolve_vecteezy_download`, endpoint `/resources/{id}/download?file_type=…`), nunca al buscar. El plan gratuito no permite elegir tamaño: muchos videos son `.mov` de 0.8–2 GB → la búsqueda **descarta videos > 250 MB (y fotos > 60 MB)** y prefiere `mp4`. Las dimensiones salen de `file_metadata.available_download_sizes` (entrada `original`). El plan gratuito **exige atribución**: la respuesta trae `requires_attribution` y `required_attribution_url`; se guarda "Título[:90] / Vecteezy" y el enlace (reemplazando el host `api.vecteezy.com` por `www.vecteezy.com`, porque el del API da 404).
- Descartado: **Magnific/Freepik** (API de pago sin plan gratuito, documentación incompleta). No hay integración.

### 6.6 `gui/workers.py`
`run_task(owner, fn, on_done, on_fail, on_progress=None)`: ejecuta `fn()` (o `fn(progress_emit)` si hay `on_progress`) en un `QThread` hijo de `owner`. **Reglas críticas:**
1. `on_done`/`on_fail`/`on_progress` deben ser **métodos enlazados de un QObject** (así llegan al hilo de la GUI). **Una lambda se ejecuta en el hilo trabajador y tocar widgets desde ahí cierra la app con una violación de acceso** (fue un bug real).
2. La tarea se guarda en el conjunto global `_ALIVE` hasta que el hilo termina; sin eso el recolector la destruye antes de ejecutarse (bug real: el render quedaba en "Preparando…" para siempre).
3. Las excepciones llegan como `str(exc)` a `on_fail` (si está vacío, el traceback). `proc.Cancelled` llega como `proc.CANCELLED`.

### 6.7 `gui/frame_preview.py`
`compose_preview(project_dir, scene, sub, height, video_frame=None, orientation="portrait", max_width=None) -> QPixmap | None`: dibuja con QPainter el cuadro 9:16 o 16:9 de la escena **sin FFmpeg**: encuadre (`fill_9_16`, `4_3_blur` centrado, `fit_blur`; el fondo difuminado es una aproximación: reducir muy pequeño, ampliar suave y oscurecer) y subtítulos (primer bloque del diálogo o `SAMPLE_TEXT`; mismo `wrap_width_for`/`caption_chunks` que el render; contorno con `QPainterPath`). Devuelve `None` si no hay recurso o imagen legible. Para videos usa `video_frame` (fotograma en el segundo `start`) o la miniatura `media["thumb"]`.
- **Calibración medida contra libass:** la altura de línea de libass = tamaño del estilo; por eso el tamaño de letra de Qt se calcula como `round(size*k*100 / metrics.height)` con una fuente de 100 px (ancho de texto coincide ≈ 2 % con el render). Posiciones: abajo = borde inferior del bloque a `1920 - margin_v(420)`, centro = centrado vertical, arriba = tope a `TOP_MARGIN = 260`. Si cambias estilos ASS en `project.py`, **cambia también aquí** (`TOP_MARGIN`, márgenes, contorno).

### 6.8 `gui/media_dialog.py` — modal de recursos
`MediaDialog(project_dir, parent=None, initial_query="")`; tras `exec()`, `dialog.media` es el `media_dict` elegido o `None`.
- **Pestaña "Buscar en bancos"**: combo editable con historial (`load_search_history`; al elegir un término busca; `add_search_term` al buscar), menú de bancos con casillas (todos activos por defecto), tipo (Videos / Imágenes / Ambos), casilla "Solo verticales" (**desactivada por defecto** por pedido del usuario), parrilla de iconos con **selección múltiple por clic** (`MultiSelection`, borde azul), vista previa en video al pasar el mouse 0.5 s (`_PreviewPopup`, ventana flotante muda en bucle), botón **"Descargar (N)"**. Si hay recursos de Vecteezy entre los marcados, pregunta antes (consumen cuota). La descarga corre en un hilo, **uno a uno**: un fallo no detiene los demás; cada archivo se guarda en `assets/`, se le crea miniatura y se registra en `assets/library.json`. Al terminar salta a la pestaña 2 con lo descargado. **No asigna nada a la escena.**
- **Pestaña "Desde mi equipo"**: parrilla de los archivos de `assets/` (`list_assets`), botones **"Elegir archivo…"** (acepta varios, los copia con `import_media`, crea miniaturas y los lista; **no cierra** el modal) y **"Usar recurso"** (o doble clic) que devuelve el `media_dict` conservando créditos si venía de un banco. Miniaturas de videos antiguos que falten se generan en segundo plano una sola vez (`thumbs_tried`).
- Mientras descarga/busca (`busy`): se deshabilitan botones y pestañas y `done()` ignora el cierre.

### 6.9 `gui/studio.py` — ventana principal
`StudioWindow(projects_dir=PROJECTS_DIR)` + `SceneCard`. Layout: `QSplitter` horizontal con tres paneles; el tercero es un `QSplitter` vertical (detalle arriba, **registro redimensionable** abajo).
- **Panel izquierdo (`general_panel`)**: grupo *Proyecto* (combo de proyectos por fecha de modificación, "Nuevo proyecto…"), *Opciones generales* (formato por proyecto: vertical 9:16 u horizontal 16:9; canal, voz, música activada + volumen 0-100 %, archivo de música con "Elegir archivo…"/"Usar la del canal", **"▶ Escuchar música"** que suena al volumen del slider y lo sigue en vivo, outro activado + "Elegir outro…"/"Usar el del canal"), *Ajustes de la voz* (velocidad −50…+50 %, tono −30…+30 Hz, volumen −50…+50 %, "Restablecer", "▶ Probar voz"), *Subtítulos* (fuente `QFontComboBox`, tamaño 30-250, color de texto y de contorno, negrita, muestra).
- **Panel central (`scenes_panel`)**: título del proyecto, "Pegar guion…", lista de `SceneCard` (diálogo editable, miniatura que abre el modal, tiempo extra, casilla para seleccionar escenas de vista previa, ↑ ↓ ✕) y "+ Añadir escena". Cada tarjeta muestra la duración estimada. El botón reproduce en orden el bloque consecutivo marcado (o solo la escena actual si no hay selección).
- **Panel derecho (`detail_body` + registro)**: vista previa (`QStackedWidget`: página 0 = cuadro estático de `compose_preview`; página 1 = `QVideoWidget` con la vista previa en video, con ⏸/▶, barra de posición y clic para pausar), "Elegir o cambiar imagen / video…", botones de vista previa, encuadre, movimiento e intensidad (solo imágenes; imagen fija, zoom, paneo vertical/horizontal y zoom lateral), inicio del video (solo videos), casilla de subtítulos y posición, grupo "Texto en imagen" por escena (texto, posición arriba/centro/abajo, tamaño y color; usa la fuente y contorno de subtítulos del proyecto), duración estimada total, "Renderizar video", botones para abrir el render, barra de progreso + **Cancelar**, registro `log`.
- **Estado y convenciones internas:**
  - `self.loading`: `True` mientras se cargan widgets desde el modelo; los *handlers* (`_options_changed`, `_scene_options_changed`, …) hacen `return` si está activo. **Todo código que asigna valores a widgets debe envolverse en `loading = True/False`.**
  - `_changed()`: marca cambio → `save_timer` (500 ms, guarda `project.json`) y `frame_timer` (120 ms, redibuja el cuadro).
  - `_settings_changed()`: igual que `_changed()` pero marca `settings_dirty`; en `_save_now()` eso dispara `remember_channel_defaults` (los ajustes de voz/subtítulos/música/outro se recuerdan **solo cuando el usuario los cambia**, no al abrir un proyecto viejo). Los handlers de ajustes de canal llaman `_settings_changed()`; los de escena llaman `_changed()`.
  - `_set_busy(bool)`: **bloquea** `general_panel`, `scenes_panel` y `detail_body` (el registro y la fila de progreso siguen activos), muestra/oculta la fila de progreso + Cancelar, pone cursor de espera, detiene la música y reinicia `proc.reset()`. `closeEvent` rechaza cerrar mientras `busy`. Se usa en render, vista previa de escena y "Probar voz".
  - `_cancel()` → `proc.cancel_all()`; los *handlers* de fallo llaman `_was_cancelled(error)` para mostrar "Proceso cancelado." sin diálogo de error.
  - Editar el modelo en memoria y **guardar antes** de cualquier render (`_save_now()`), porque `render_project` relee de disco.
  - `QMessageBox`/`QInputDialog` usan enums completos (`QMessageBox.StandardButton.Yes`); en PySide6 6.12 pasar enteros (`setCheckState(2)`) lanza `TypeError`.
- **Arranque (`main()`)**: en Windows fija `AppUserModelID = "Genxapp.VideoFactory"` (la barra de tareas muestra el icono propio, no el de Python), `app.setStyle("Fusion")`, `app.setWindowIcon(assets/video_factory.ico)`, instala el `excepthook` y abre la ventana. `_open_initial_project` abre el proyecto más reciente o crea uno ("Mi video") con el último canal usado.

---

## 7. Pipeline de render (`project.render_project`)

Entrada: carpeta del proyecto. Salida: `render/video.mp4` (o `render/preview/scene.mp4` con `only_scene`) + informe.

1. `load_project`; en vista previa solo la escena indicada; valida que cada escena tenga `media` y que el archivo exista (`FileNotFoundError("La escena N no tiene un recurso visual válido.")`) y que exista `data/tts-packages` si hay diálogo.
2. Estilos ASS: `Default` (abajo, alineación 2), `Middle` (5, MarginV 0), `Top` (8), con fuente/tamaño/colores del proyecto. Cabecera y dimensiones son 1080×1920 en `portrait` (predeterminado y migración para proyectos antiguos) o 1920×1080 en `landscape`; en horizontal el tamaño de subtítulo se escala a 72 % y los márgenes se adaptan.
3. **Por escena** (se llama `progress(número, total)`):
   - **Voz**: `synthesize_voice` (caché). `length = duración_wav + 0.35 + extra_seconds`. Sin diálogo: `length = scene["duration"] + extra_seconds` y audio silencioso (`anullsrc`). El tiempo extra queda como imagen sostenida y audio en silencio después de la voz.
   - **Audio de escena**: `scene-NNNN.wav` temporal con `apad` hasta `length`.
   - **Video de escena** (`scene-NNNN.mp4`, sin audio):
     - Encuadre con `_frame_graph(crop, k, orientation)`: llenar el cuadro, `4_3_blur` (fondo difuminado + ventana 4:3 centrada), `fit_blur` (fondo difuminado + imagen completa). `k = 2` en render final y `k = 1` en vista previa.
     - **Imágenes con movimiento**: la foto se ajusta una sola vez a un PNG del tamaño `k`; zoom y paneos usan **`perspective` con `eval=frame` e `interpolation=cubic`**, con coordenadas subpíxel para evitar temblor. `motion` admite imagen fija, acercar/alejar, paneo arriba/abajo/izquierda/derecha y zoom lateral; el recorrido se calcula sobre el cuadro de `orientation`, tanto vertical como horizontal. *No sustituir por `zoompan`: redondea posiciones a píxeles enteros y el movimiento puede vibrar.*
     - Imágenes sin zoom y videos: `_frame_graph(...)` directo. Videos: `-stream_loop -1 -ss start` (si el clip es más corto que la voz, **se repite en bucle**).
     - Codificación: `libx264 crf 18 preset medium` (vista previa: `crf 28 veryfast`).
   - **Texto en imagen**: si `text_overlay.text` no está vacío, se añade un estilo ASS propio por escena y un evento que cubre toda su duración; posición, tamaño y color son configurables y la fuente/contorno usan los ajustes generales de subtítulos.
   - **Subtítulos**: el diálogo se parte en bloques (`caption_chunks(…, wrap_width*2)`), cada bloque dura proporcional a su número de palabras dentro de `length - 0.35`; el texto se ajusta con `textwrap.wrap(width=wrap_width)` y se une con `\N`; se omiten si `show_subtitles` es falso; el estilo depende de `subtitle_pos`. Los tiempos acumulan `cursor` (suma de `length`).
4. **Ensamblado para proyectos largos**: `_write_concat_list` genera listas de archivos para el concat demuxer de FFmpeg. Une por copia de flujo los clips de video y presenta los WAV de voz mediante una segunda lista de concat, sin crear otro WAV gigante. Esto mantiene pequeño el número de entradas y la longitud del grafo de filtros aunque haya muchas escenas. La guía oficial exige streams compatibles en las partes concatenadas; todas las escenas se producen con la misma resolución, FPS y códec. Luego se queman subtítulos; **música** (si `music.enabled` y el archivo existe; se repite con `-stream_loop -1`, se recorta a la duración total, `volume = gain`, **fade-out de 3 s al final**) se mezcla con la voz; **outro** (solo render final; si `project.outro` y el archivo existe) se escala/recorta al tamaño de `orientation`, y si no tiene audio se genera silencio; se concatena video y audio. La duración permitida para las etapas de audio/video crece con la duración calculada del proyecto, y el ensamblado se muestra como progreso indeterminado. Salida H.264 high, yuv420p, 30 fps, 8 Mb/s (vista previa 2 Mb/s), AAC 192 kb/s 48 kHz, `+faststart`.
5. **Escritura atómica y temporales**: FFmpeg escribe a `video.part.mp4` y se hace `os.replace` solo si terminó bien; un render cancelado o fallido **nunca deja un video roto ni pisa el anterior**. Los intermedios van a un `render/.work-<id>/` único y se borran al completar; si el render falla se conservan para diagnóstico. `captions.ass` sigue junto al MP4 final.
6. Render final: copia `creditos.txt` a `render/`, calcula avisos (duración a más de 5 s de los 45 s objetivo; sin música; sin outro) y escribe `render/render.json`: `{"status","output","duration_seconds","target_seconds","scenes":[…],"warnings","rendered_at"}`.
7. Tiempos de referencia (equipo del usuario): un video de ~16 s con 2 imágenes con zoom ≈ 80–120 s con las voces ya en caché; la primera síntesis de voz por escena toma unos segundos y necesita Internet.

---

## 8. Flujos de usuario → código

- **Crear proyecto** (`new_project`): pide nombre (y canal, con el último usado por defecto) → `create_project` → aplica los ajustes guardados del canal → `open_project`.
- **Cambiar de canal** (`_channel_changed`): para la música; si hay ajustes guardados del canal los aplica (`apply_channel_defaults`), si no usa los presets de `CHANNELS`; recarga widgets; `_options_changed` los vuelve a recordar.
- **Elegir recurso**: miniatura de la escena o botón → `pick_media(index)` → `MediaDialog` → si devuelve `media`, se asigna a la escena, se refresca la tarjeta y el cuadro, `_changed()`.
- **Descargar varios** → quedan en `assets/` + `library.json`; se usan luego desde la pestaña 2.
- **Vista previa del cuadro** (automática): `_refresh_frame` → `compose_preview`; para videos, `_video_frame` extrae en segundo plano el fotograma del `start` (caché `render/frames/<stem>_<start:.1f>.jpg`) y refresca al terminar; si el segundo no existe, avisa en el registro y deja la miniatura.
- **Vista previa** (botón): `_save_now` → `render_project(only_scene=i)` para una escena o `render_project(only_scenes=[...])` para el bloque consecutivo marcado, en hilo → reproduce el MP4 guardado en `render/preview/cache/` (con música; sin outro). La huella incluye datos de las escenas, ajustes globales y fecha/tamaño de recursos; si coincide, retorna la vista sin renderizar. El botón "Volver a renderizar" pasa `force_preview=True`. Las selecciones no consecutivas se rechazan con un aviso.
- **Renderizar**: `_save_now` → `_set_busy(True)` → `run_task(render_project, …)`; progreso por escena; cancelable.
- **Probar voz**: `synthesize_voice` con una frase fija y los ajustes actuales; reproduce con `test_player`.
- **Música/outro propios**: `import_shared(canal, archivo)` y se guarda la referencia `shared:` en el proyecto; `remember_channel_defaults` la convierte en el valor por defecto del canal. **Un proyecto depende de `data/channel_defaults/`**: si se mueve el proyecto a otro PC sin esa carpeta, el render avisa "Sin música de fondo: no existe …" y continúa sin ella.

---

## 9. Decisiones de diseño y su porqué

| Decisión | Motivo |
|---|---|
| Interfaz de una sola pantalla tipo storyboard (estilo CapCut) con escenas | Pedido del usuario: las pestañas antiguas (Inicio, Crear trabajo, Trabajos, Configuración) le parecieron inútiles; todo debe girar alrededor de la escena |
| Guion libre en vez de catálogo | El catálogo limitaba los temas; ahora cualquier guion funciona |
| Duración de escena = duración de su voz | Sincronía exacta de cortes y subtítulos (antes se repartía por palabras) |
| Voz por escena con caché por hash | Re-renders rápidos; solo se vuelve a sintetizar la escena que cambió |
| `perspective` en lugar de `zoompan` | El usuario percibió temblor; se midió y se eligió la opción 5× más estable |
| Foto ajustada una vez a PNG y luego zoom | Con fotos de 7000 px el render tardaba ~9 min; ahora segundos por escena |
| Render a `.part.mp4` + `os.replace` | La cancelación no puede dejar videos corruptos |
| `proc.run` propio | Sin ventanas de consola con `pythonw` y con cancelación real |
| Bloquear la UI durante procesos | Pedido del usuario; evita estados inconsistentes y cierres a medias |
| Música/outro compartidos por canal (`shared:`) | Pedido del usuario: "cosas que se reutilicen en cada proyecto" sin duplicar archivos; costo: el proyecto deja de ser autónomo |
| Ajustes recordados por canal solo al cambiarlos | Que abrir un proyecto viejo no pise los ajustes "últimos" del canal |
| Vista previa del cuadro dibujada con Qt (no FFmpeg) | Respuesta inmediata al mover cualquier control; calibrada contra el render real |
| Tamaño de subtítulo duplicado + ajuste de líneas por tamaño | El usuario los veía muy pequeños; con letra grande hay que partir en bloques cortos para que no se salgan de 1080 px |
| Descargas de bancos solo al pulsar "Descargar" | Respeta cuotas (Vecteezy) y la regla original: revisión humana antes de descargar |
| Créditos automáticos por proyecto | Pedido del usuario; varias licencias exigen atribución |

---

## 10. Trampas conocidas (léelas antes de modificar)

1. **Hilos Qt**: callbacks de `run_task` = métodos enlazados (nunca lambdas); mantener referencia de la tarea (`_ALIVE`).
2. **PySide6 6.12**: enums completamente calificados (`Qt.CheckState.Checked`, `Qt.ItemDataRole.UserRole`, `QMessageBox.StandardButton.Yes`).
3. **`loading`**: asignar widgets sin activarlo dispara handlers y puede corromper el modelo.
4. **Juego de `eventFilter`**: los `installEventFilter(self)` deben ir **después** de crear los atributos que el filtro usa (`self.video`, `self.preview`); si no, `AttributeError` durante la construcción.
5. **`QLabel` con pixmap**: su tamaño mínimo sugerido es el del pixmap y bloquearía reducir la ventana; por eso `self.preview.setMinimumSize(120, 380)` explícito.
6. **QtMultimedia**: `QMediaPlayer` mantiene abierto el archivo; antes de regenerar un MP4 hay que `stop()` y `setSource(QUrl())` (`_stop_preview`). `QVideoWidget` no aparece en `widget.grab()` (las capturas de pantalla no lo muestran).
7. **Fuentes en pruebas**: el plugin Qt `offscreen` no tiene fuentes del sistema → métricas falsas. Probar con `QT_QPA_PLATFORM=windows`.
8. **libass/ASS**: el salto de línea es la secuencia literal `\N`; las llaves `{}` del texto se reemplazan por paréntesis; los colores van en `&H00BBGGRR`. Los estilos `Middle`/`Top` existen siempre aunque no se usen.
9. **`filter_complex` y rutas**: la ruta de `captions.ass` se escapa (`\`→`/`, `:`→`\:`, `'`→`\'`).
10. **Hash de voz**: cambiar los parámetros que entran al hash invalida toda la caché (se vuelve a sintetizar).
11. **Wikimedia/Openverse/NASA** pueden devolver 429/errores intermitentes; los fallos de un banco no deben tumbar la búsqueda (ya manejado).
12. **Vecteezy**: no resolver la URL de descarga al buscar (gasta cuota); respetar los límites de tamaño; el host de la URL de atribución se corrige a `www`.
13. **Windows**: `tzdata` imprescindible; `taskkill` para árboles de procesos; las rutas del usuario tienen espacios (`D:\Adrian\Redes sociales\…`) → siempre pasar listas de argumentos, nunca cadenas de shell.
14. **Herramienta de edición del asistente**: al escribir parches con secuencias `\n` dentro de *heredocs* de shell los escapes se corrompen; para editar código con barras invertidas usar la herramienta de edición de archivos, no scripts por stdin.
15. **No usar `subprocess` directo** en la app: usar `proc.run`.
16. `_rank` ordena por (penalización de verticalidad, penalización de duración, distancia a 9:16); en `search_media` se usa solo el primer componente para mezclar bancos.

---

## 11. Cómo extender (recetas)

### Añadir un banco de recursos
1. En `stock_sources.py`: función `search_<banco>(query, kind, vertical_only=False) -> list[dict]` que devuelva dicts con `_item("<Banco>", kind, id, …)` (campos de §5.4). Rellenar siempre `license`, `license_url`, `attribution`, `author`, `page_url`; `preview_url` (miniatura); `preview_video_url` si hay mp4 corto; `width/height` si se conocen.
2. Registrar en `SOURCES` (tipos soportados) y en `_SEARCHERS`.
3. Si la URL de descarga hay que resolverla (cuota, firma): dejar `download_url=""` y añadir la rama en `clips.download_media` (patrón de Vecteezy), actualizando `item["license"]/["attribution"]` en la resolución.
4. Claves en `.env`: leer con `load_env_file()` + `os.getenv`; documentar en `.env.example` y `README.md`. Nunca imprimir claves.
5. Respetar límites de tamaño; manejar errores con `RuntimeError` de mensaje claro en español.
6. La GUI lo muestra sola (el menú "Bancos" se arma desde `SOURCES`). Actualizar el título de pestaña de `media_dialog` si quieres listarlo.
7. Probar con una búsqueda y una descarga reales (y registrar en este documento las peculiaridades).

### Añadir un canal
`channels.CHANNELS[clave] = {label, music (Path|None), music_gain, outro (Path|None), subtitles{font,size,color,outline,bold}, default_voice}`. Colocar los archivos en `Canal/`. La GUI (combos de canal) y los ajustes recordados lo soportan sin más cambios.

### Añadir una voz
Entrada en `channels.VOICES` (`label`, `voice` Edge, `rate`, `pitch`, `gender`). Verificar el nombre con `edge_tts.list_voices()`.

### Añadir un ajuste **por escena**
1. Clave en `new_scene()` y lectura con `scene.get("clave", default)` en todos los usos.
2. Widget en el formulario de `_build_detail`; conectar a `_scene_options_changed`; cargarlo en `select_scene` (dentro de `loading`); guardarlo en `_scene_options_changed`.
3. Usarlo en `render_project` (y en `frame_preview.compose_preview` si afecta lo que se ve).
4. Si afecta el cuadro estático, `_changed()` ya redibuja.

### Añadir un ajuste de **proyecto/canal** (voz, música, subtítulos, outro…)
1. Valor por defecto en `create_project` y migración con `setdefault` en `load_project`.
2. Widget en `_build_general`; handler que modifique `self.project[...]` y llame a **`_settings_changed()`** (para recordarlo por canal); cargarlo en `open_project` y `_channel_changed`.
3. Si debe recordarse por canal: añadirlo a `remember_channel_defaults` y `apply_channel_defaults`.
4. Usarlo en `render_project`.

### Añadir una opción de encuadre
`project.CROPS` (clave→etiqueta), rama nueva en `_frame_graph` (render) **y** en `frame_preview._draw_frame` (vista previa). El combo de la GUI se llena desde `CROPS`.

### Añadir una velocidad de zoom
Entrada en `ZOOM_SPEEDS` y en `studio.ZOOM_LABELS`.

### Añadir un proceso largo/bloqueante
Ejecutarlo con `run_task(self, fn, self._ok, self._fail[, self._progress])` (métodos enlazados); `_set_busy(True)` al empezar y `False` en ambos *handlers*; en el de fallo, `if self._was_cancelled(error): return`; ejecutar programas externos con `proc.run` para que Cancelar funcione; para salidas de archivo usar el patrón `.part` + `os.replace`.

### Añadir un diálogo
Seguir `MediaDialog`: parent = ventana, `busy` para impedir cerrar durante hilos, callbacks como métodos.

---

## 12. Pruebas: cómo se verificó y qué falta

**No hay suite de pruebas automatizadas en el repo.** Todo se verificó con scripts ad-hoc (en la carpeta temporal de la sesión, no versionados) ejecutados con el Python del venv. Patrones útiles:
- Para ejercitar la GUI sin interacción: crear `QApplication`, instanciar `StudioWindow(carpeta_temporal)`, llamar métodos (`render()`, `select_scene(i)`, `pick_music()`), bombear eventos con `app.processEvents()` hasta que `window.busy` sea falso, y guardar capturas con `widget.grab().save(...)`. Usar `QT_QPA_PLATFORM=windows` (no `offscreen`) si importan las fuentes.
- Parchear `QMessageBox.critical/warning`, `QInputDialog.getText/getItem`, `QFileDialog.getOpenFileName(s)`, `QColorDialog.getColor` para que no bloqueen.
- **Siempre** parchear `video_factory.project.DEFAULTS_FILE` a una carpeta temporal para no tocar `data/channel_defaults.json` ni `search_history.json` reales, y usar `projects_dir` temporal.
- Medir en vez de suponer: p. ej. el temblor del zoom se midió extrayendo una fila de cada fotograma y calculando el desvío respecto a un ajuste lineal; la calibración de subtítulos se hizo comparando el ancho de texto del render con `QFontMetricsF`.
- Verificar visualmente con capturas y con `ffmpeg` (extraer fotogramas, `volumedetect`, `ffprobe`/`ffmpeg -i` para duraciones y pistas).

**Verificado en el equipo del usuario (Windows 10):** búsqueda y descarga reales en Pixabay, NASA, Wikimedia Commons, Openverse y Vecteezy; render completo con voz, música, outro, zoom, subtítulos en las tres posiciones, cancelación a mitad de render, vista previa de escena, ajustes recordados por canal, música/outro compartidos, historial, selección múltiple.
**No verificado / pendiente de confirmación:** icono en la barra de tareas y ausencia total de ventanas de consola (se comprobó en código y por programa, no a ojo); legibilidad del icono a 16 px; instalación desde cero en un PC limpio (se probó `instalar.bat` en el equipo ya instalado; en Windows 11 el usuario reportó que la app no abría; se corrigió la causa probable —`tzdata`— pero el usuario no confirmó que ya funcione ahí); Pexels (la clave del usuario da 401).

---

## 13. Historial de lo realizado (cronológico)

**Antes de esta serie de sesiones** (según `requerimientos.md`): proyecto Python original basado en catálogo (`pipeline.py`, `catalog.py`, TTS con edge-tts, FFmpeg); etapa 1 = GUI PySide6 con pestañas; etapa 2 = búsqueda en Pexels/Pixabay con aprobación manual y manifiesto; bug de `tzdata`; confusión de rutas (`D:\Adrian\Redes sociales\video_factory` vs `…\Gui_Video_factory\video_factory_gui_mvp`, esta última es la vigente).

**Sesiones de octubre de 2026 (12–23):**
1. **Revisión del estado** y primer montaje (etapa 3) conectando clips descargados al render; se descubrió y corrigió el bug de enums de PySide6 que ocultaba los resultados de búsqueda; miniaturas, vista previa al pasar el mouse, grilla de columnas adaptativas, filtro de verticales, búsqueda de imágenes, archivos propios.
2. **Voces y canales**: instalación de `edge-tts` en `data/tts-packages`; canales "Qué curioso…¿no?" (voz masculina Gonzalo) y "Belleza con evidencia" (voz femenina Dalia, subtítulos violeta, música propia); se copiaron música y outro del usuario a `Canal/`.
3. **Acceso directo e icono**, corrección del cierre de la app al terminar tareas (callbacks en hilo), pestaña de configuración con estado de claves/FFmpeg.
4. **Rediseño completo** (pedido del usuario con una captura de CapCut): ventana única, escenas con diálogo + recurso, modal para elegir recurso, opciones generales a la izquierda, duración determinada por el guion. `project.py` y render por escena; ventana `studio.py`; modal `media_dialog.py`.
5. **Zoom sin temblor** (medición y cambio a `perspective`), música propia, ajustes de subtítulos (fuente/tamaño/color, tamaños duplicados), vista previa de escena en video, pausa, registro redimensionable.
6. **Más bancos** (NASA, Wikimedia, Openverse) y `creditos.txt` automático; **instalador** `instalar.bat`; **repositorio Git** y primer push (commits `7bbd8eb`, `09da194`…).
7. **Vecteezy** (con documentación OpenAPI que pegó el usuario y su clave en `.env`); Magnific evaluado y descartado.
8. **Robustez**: `tzdata` + `excepthook` con `error.log` (fallo en Windows 11), posición de subtítulos por escena, casilla de mostrar/ocultar subtítulos, botón de abrir carpeta del video, "Solo verticales" desactivado por defecto.
9. **Voz**: ajustes de velocidad/tono/volumen, "Probar voz", voces neutrales (Alonso, Paloma) y Jorge/Salomé.
10. **Vista previa viva del cuadro** (encuadre + subtítulos con Qt, calibrada contra libass) y del segundo de inicio de los videos.
11. **Icono nuevo** (multi-tamaño, generado por `assets/make_icon.py`), icono en barra de tareas (`AppUserModelID`), consolas ocultas (`proc.run`), bloqueo de la UI durante procesos, **cancelar** con escritura atómica del video, botón de **escuchar música** (con volumen del slider).
12. **Ajustes recordados por canal** y **música/outro compartidos** (`shared:`), outro propio.
13. **Historial de búsquedas, selección múltiple con "Descargar" y pestaña de archivos del proyecto** con `library.json`.
14. **Salida horizontal 16:9 para videos largos** con ensamblado temporal por partes; ahora cada escena admite un título opcional de capítulo y el proyecto guarda datos de publicación de YouTube. El render deja `youtube_metadata.txt` con descripción y capítulos si las marcas cumplen las reglas vigentes; la app todavía no sube ni programa videos.
15. **Movimientos documentales en imágenes**: presets por escena de zoom, paneo vertical/horizontal y zoom lateral; son iguales para 9:16 y 16:9 y usan interpolación cúbica subpíxel.

**Commits** (de más antiguo a más reciente): `7bbd8eb` estudio por escenas · `09da194` Vecteezy · `53a4ce5` arreglo Windows limpio + error log · `bc978e8` subida web de `Canal/*` (del usuario) · `80faab7` posición de subtítulos + abrir carpeta · `61ed21e` casilla de subtítulos por escena · `e7e8ec2` ajustes de voz y voces nuevas · `96fbb4e` vista previa viva · `d124c6d` cancelar/bloqueo/consolas/icono · `1d69b45` botón de música · `7914985` música con volumen del slider · `d612962` ajustes por canal y archivos compartidos · `2fbc817` historial, multi-descarga y pestaña de archivos.

---

## 14. Estado actual, límites y backlog sugerido

**Límites conocidos**
- Un solo recurso visual por escena (el modelo `scene["media"]` es un dict, no una lista).
- La duración total depende del guion; el objetivo de 45 s solo genera un aviso.
- Si el clip de video es más corto que la voz de su escena, se repite en bucle (no se congela el último fotograma).
- Los videos de la vista previa/estática usan la miniatura (640 px; las antiguas, 320 px) y un fondo difuminado aproximado.
- Música sin "ducking" (no baja automáticamente bajo la voz); el volumen es fijo por proyecto.
- Windows únicamente; requiere Internet para la voz neuronal y los bancos.
- Las descargas del modal no son cancelables (solo los procesos de FFmpeg/TTS).
- Los proyectos con música/outro compartidos dependen de `data/channel_defaults/`.
- Sin pruebas automatizadas.
- `README_ETAPA2.md`, `requerimientos.md`, `video_factory/README_GUI.md` y varios módulos originales están obsoletos/heredados; podrían limpiarse (el usuario no lo pidió).

**Ideas no implementadas / consultadas**
- Generación de imágenes con IA (OpenAI de pago, o servicios gratuitos por verificar) y de video con IA (no hay opción gratuita fiable por API; los modelos abiertos requieren GPU).
- Otros bancos con API gratuita (p. ej. Coverr; requiere solicitar acceso).
- Varios recursos por escena, transiciones entre escenas, ducking de música, perfiles de calidad y optimizaciones para proyectos largos. La salida admite ahora 9:16 y 16:9.
- Automatización de subida y programación de videos a YouTube, TikTok y Facebook (cada plataforma requiere integración propia).
- Un tercer canal (hay que agregarlo en `channels.py` y subir sus archivos a `Canal/`).
- Catálogo de temas para el canal Belleza (el canal solo cambia presentación; los guiones los escribe el usuario).

---

## 15. Checklist antes de entregar un cambio

1. ¿Los campos nuevos de `project.json`/escena tienen migración (`setdefault`/`.get`)?
2. ¿Los callbacks de hilos son métodos enlazados y se usa `_set_busy`/`_was_cancelled` si es un proceso largo?
3. ¿Los subprocess pasan por `proc.run`?
4. ¿Si cambia lo que se ve (encuadre, subtítulos), se actualizó también `frame_preview.py`?
5. ¿Se probó con datos temporales (parcheando `DEFAULTS_FILE`) y se verificó con captura o medición?
6. ¿Los textos de la UI están en español y el código/docstrings en inglés?
7. ¿No se imprimieron ni versionaron claves?
8. ¿Se actualizó este documento y `README.md` si cambió algo estructural?
9. Commit en inglés, imperativo, con `Co-Authored-By`; **solo si el usuario lo pidió**; `git pull --rebase origin main` si el push es rechazado.
