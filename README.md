# Video Factory

Aplicación de escritorio (Windows, PySide6) para producir videos verticales 9:16 por escenas: guion libre, voz neuronal por escena, imagen o video por escena, subtítulos, música de fondo y créditos automáticos.

## Instalación
1. Instala Python 3.11 o superior (marca "Add python.exe to PATH").
2. Ejecuta `instalar.bat`: crea el entorno virtual, instala PySide6 y `edge-tts`, instala FFmpeg con winget si falta y crea el acceso directo en el Escritorio.
3. Copia `video_factory/.env.example` a `video_factory/.env` y escribe tus claves de Pexels y Pixabay y, si la tienes, el ID de cuenta y la clave de Vecteezy (todas opcionales; NASA, Wikimedia Commons y Openverse no necesitan clave). **Nunca subas `.env` al repositorio.**
4. Copia a `Canal/` la música y el outro de tus canales (ver `Canal/LEEME.txt`).

## Uso
`python -m video_factory.gui` o el acceso directo "Video Factory".

- Panel izquierdo: proyecto, canal, voz, música (del canal o un archivo propio) y estilo de subtítulos.
- Centro: escenas con su diálogo y su imagen o video; "Pegar guion…" parte un texto en escenas.
- Derecha: encuadre, zoom, vista previa de la escena y render final.
- Cada proyecto vive en `data/projects/<nombre>/` e incluye `creditos.txt`, que se actualiza al elegir recursos de bancos.

## Estructura
- `video_factory/project.py`: modelo de proyecto, render por escenas y créditos.
- `video_factory/stock_sources.py` y `clips.py`: búsqueda y descarga en Pexels, Pixabay, NASA, Wikimedia Commons, Openverse y Vecteezy.
- `video_factory/channels.py`: canales (música, outro, subtítulos) y voces.
- `video_factory/gui/`: ventana única (`studio.py`), selector de recursos (`media_dialog.py`) y tareas en segundo plano (`workers.py`).
- `video_factory/pipeline.py`, `catalog.py`, `storage.py` y demás: módulos originales del proyecto, conservados.
