# Video Factory GUI — primera versión

## Archivos añadidos
- `video_factory/gui/__init__.py`
- `video_factory/gui/__main__.py`
- `video_factory/gui/main_window.py`
- `requirements-gui.txt`

La GUI usa el pipeline y el catálogo ya existentes; no sustituye el CLI.

## Instalación en Windows
Abre PowerShell en la carpeta que contiene la carpeta `video_factory` (la raíz del proyecto).

```powershell
py -m pip install -r requirements-gui.txt
```

Si el comando `py` no existe, prueba `python -m pip install -r requirements-gui.txt`.

## Ejecutar
Desde la raíz del proyecto:

```powershell
py -m video_factory.gui
```

## Qué incluye esta versión
- Inicio y registro de mensajes.
- Crear un trabajo usando una idea existente en `catalog.py`.
- Ver los trabajos guardados.
- Ejecutar el pipeline actual para generar artefactos.
- Intentar renderizar el MP4 con FFmpeg si el trabajo tiene los recursos requeridos.
- Elegir otra carpeta de datos.

## Importante
Esta es la primera interfaz conectada al pipeline existente, no la automatización completa de búsqueda de clips. La búsqueda de Pexels/Pixabay, los subtítulos desde audio, y la edición de escenas se deben integrar en etapas posteriores. Los temas nuevos deben incorporarse al catálogo con fuentes verificables; el pipeline no inventa un dossier factual para cualquier tema.
