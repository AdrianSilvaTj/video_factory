# Video Factory — Etapa 2: búsqueda y revisión de clips

## Qué añade
- Nueva pestaña **Bancos de clips** en la GUI existente.
- Búsqueda en las APIs oficiales de Pexels y Pixabay.
- Sugerencia automática de hasta 8 resultados, priorizando proporción vertical cercana a 9:16 y duraciones útiles.
- Revisión manual: puedes marcar/desmarcar resultados. **No descarga nada hasta pulsar “Aprobar y descargar seleccionados” y confirmar.**
- Descargas en la carpeta del trabajo y manifiesto `clips_manifest.json` con proveedor, autor, URLs, licencia, consulta, dimensiones y aprobación.
- Objetivo de montaje registrado: 45 segundos totales; la selección de clips no significa que el montaje final ya esté conectado al renderizador existente.

## Archivos que debes copiar
Cierra Video Factory primero. Descomprime este parche y copia el contenido de la carpeta `video_factory` sobre `D:\Adrian\Redes sociales\video_factory`, conservando los archivos existentes. Este parche **añade** `clips.py`, `gui\clips_panel.py`, `.env.example` y `requirements-stage2.txt`, y actualiza `gui\main_window.py` para añadir la pestaña y el texto de configuración. No reemplaza `pipeline.py`, `catalog.py`, `storage.py` ni otros módulos del proyecto.

Si Windows pregunta si deseas reemplazar `gui\main_window.py`, elige sí (ese archivo sí contiene la integración de la pestaña). Los demás archivos nuevos no deberían existir todavía.

## Configurar las claves API
1. Solicita una clave en Pexels: https://www.pexels.com/api/ .
2. Solicita una clave en Pixabay: https://pixabay.com/api/docs/ .
3. En la carpeta `D:\Adrian\Redes sociales\video_factory`, copia `.env.example` y llama a la copia `.env` (sin `.txt`). En el Explorador activa **Ver > Mostrar > Extensiones de nombre de archivo** para evitar crear accidentalmente `.env.txt`.
4. Abre `.env` con Bloc de notas y sustituye los valores de ejemplo por tus claves reales, por ejemplo `PEXELS_API_KEY=tu_clave_real`. No pongas comillas ni espacios alrededor del signo `=`.
5. No compartas el archivo `.env`, no pegues las claves en el código y no lo subas a repositorios públicos.

## Instalar y ejecutar
Abre PowerShell y ejecuta:

```powershell
cd "D:\Adrian\Redes sociales\video_factory"
# Activa el entorno virtual que ya usas para la GUI. Si se llama .venv:
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-stage2.txt
cd "D:\Adrian\Redes sociales"
python -m video_factory.gui
```

Si ejecutabas el proyecto desde otra carpeta o con otro entorno virtual, usa el mismo intérprete/entorno donde ya te funcionó la GUI; no crees otro entorno innecesariamente.

## Flujo de uso
1. En **Crear trabajo**, crea un trabajo como antes.
2. En **Trabajos**, copia el ID que aparece en la lista.
3. Abre **Bancos de clips**, pega el ID y escribe el tema de búsqueda.
4. Pulsa **Buscar y sugerir selección**. Revisa proveedor, duración, dimensiones, autor y enlace; desmarca lo que no sirva.
5. Pulsa **Aprobar y descargar seleccionados** y confirma. Los archivos se guardan en `data\jobs\ID_DEL_TRABAJO\clips\` (si la GUI usa la carpeta de datos predeterminada). El manifiesto se guarda junto a los clips.

## Limitaciones de esta etapa
- Las claves API y conexión a internet son necesarias. Si una API falla, la otra aún puede entregar resultados; el aviso aparece en el estado.
- El ranking prioriza verticales, pero no recorta ni convierte clips.
- Los 45 segundos son el objetivo global del futuro video, no la duración individual de cada clip ni una garantía de que la selección sume exactamente 45 segundos.
- Esta etapa prepara y documenta los clips, pero no modifica la lógica de `pipeline.py` ni los inserta automáticamente en el MP4. La siguiente integración conectará el manifiesto con el montaje/renderizado.
- Verifica los términos de licencia actuales antes de publicar. Conserva enlaces y créditos; que un clip aparezca en una API no significa que pueda redistribuirse como archivo independiente.

### Seguridad de las claves
Si el proyecto usa Git, añade `.env` a tu `.gitignore` existente. No reemplaces un `.gitignore` que ya tengas; solo agrega la línea `.env`.
