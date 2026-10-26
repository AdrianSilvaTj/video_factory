# Video Factory

Aplicación de escritorio (Windows, PySide6) para producir videos por escenas en formato vertical 9:16 u horizontal 16:9: guion libre, voz neuronal por escena, imagen o video por escena, subtítulos, música de fondo y créditos automáticos.

## Instalación
1. Instala Python 3.11 o superior (marca "Add python.exe to PATH").
2. Ejecuta `instalar.bat`: crea el entorno virtual, instala PySide6 y `edge-tts`, instala FFmpeg con winget si falta y crea el acceso directo en el Escritorio.
3. Copia `video_factory/.env.example` a `video_factory/.env` y escribe tus claves de Pexels y Pixabay y, si la tienes, el ID de cuenta y la clave de Vecteezy (todas opcionales; NASA, Wikimedia Commons y Openverse no necesitan clave). **Nunca subas `.env` al repositorio.**
4. La música y el outro de los canales vienen en `Canal/` (ver `Canal/LEEME.txt`).

## Uso
`python -m video_factory.gui` o el acceso directo "Video Factory".

- Panel izquierdo: proyecto, formato 9:16/16:9, canal, voz, música (del canal o un archivo propio) y estilo de subtítulos.
- Centro: escenas con su diálogo y su imagen o video; "Pegar guion…" parte un texto en escenas.
- Para las imágenes, cada escena ofrece imagen fija, zoom suave, paneo vertical u horizontal y zoom lateral. Los movimientos se aplican igual en 9:16 y 16:9 y usan el mismo recorrido subpíxel suave para evitar vibración.
- Derecha: encuadre, vista previa de la escena y render final. Usa la vista previa de escena para ver el movimiento aplicado; los intermedios de un render exitoso se limpian automáticamente para ahorrar espacio y, si falla, se conservan para diagnóstico.
- Cada proyecto vive en `data/projects/<nombre>/` e incluye `creditos.txt`, que se actualiza al elegir recursos de bancos.
- En cada escena puedes escribir un título de capítulo. El botón «Datos para YouTube…» guarda título, descripción y etiquetas del video; tras renderizar, `render/youtube_metadata.txt` incluye los capítulos que cumplen el mínimo de YouTube (inicio 0:00, al menos tres marcas y tramos de 10 s).

## Estructura
- `video_factory/project.py`: modelo de proyecto, render por escenas y créditos.
- `video_factory/stock_sources.py` y `clips.py`: búsqueda y descarga en Pexels, Pixabay, NASA, Wikimedia Commons, Openverse y Vecteezy.
- `video_factory/channels.py`: canales (música, outro, subtítulos) y voces.
- `video_factory/gui/`: ventana única (`studio.py`), selector de recursos (`media_dialog.py`) y tareas en segundo plano (`workers.py`).
- `video_factory/pipeline.py`, `catalog.py`, `storage.py` y demás: módulos originales del proyecto, conservados.
