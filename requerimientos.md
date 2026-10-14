# CONTEXTO COMPLETO DEL PROYECTO VIDEO FACTORY
## Documento de transferencia para continuar en otra sesión de ChatGPT

**Fecha de actualización:** 12 de octubre de 2026  
**Proyecto:** Video Factory  
**Objetivo:** Aplicación de escritorio para Windows que automatice progresivamente la producción de videos cortos para redes sociales.  
**Idioma de trabajo:** Español.  
**Estado actual:** La primera versión de la interfaz gráfica llegó a ejecutarse correctamente. Se preparó un parche para la etapa 2, pero la instalación y el funcionamiento de esa etapa todavía deben verificarse en el equipo del usuario.

---

# 1. OBJETIVO GENERAL

Estamos desarrollando una aplicación llamada **Video Factory** para automatizar la creación de videos cortos destinados a redes sociales, especialmente Facebook Reels, TikTok y YouTube Shorts.

La intención es aprovechar el proyecto Python existente y convertirlo en una herramienta de escritorio con interfaz gráfica, reduciendo progresivamente el trabajo manual.

La aplicación debe evolucionar hacia un flujo que permita:

1. Crear un trabajo a partir de una idea o tema.
2. Preparar el contenido del video.
3. Buscar videos de archivo relacionados con el tema.
4. Seleccionar automáticamente clips adecuados y permitir que el usuario los revise.
5. Descargar únicamente los recursos aprobados.
6. Generar una narración con voz sintética.
7. Seleccionar los fragmentos útiles de los clips.
8. Adaptar el video al formato vertical 9:16.
9. Generar subtítulos.
10. Montar las escenas, la narración y los subtítulos.
11. Producir un video final con una duración objetivo de 45 segundos.
12. Conservar información de los recursos utilizados y permitir la revisión humana antes de publicar.

La automatización debe ser progresiva. No debemos dar por implementadas las funciones que todavía no se han desarrollado o probado.

# 2. PROYECTO ORIGINAL Y MÓDULOS EXISTENTES

El usuario proporcionó un ZIP del proyecto Python original para convertirlo en una aplicación gráfica.

Entre los módulos y recursos identificados en el proyecto original se encuentran:

- `__init__.py`
- `__main__.py`
- `catalog.py`
- `cli.py`
- `compose_3d_infographics.py`
- `estilo_infografia_3d.md`
- `infographic_prompts.py`
- `pipeline.py`
- `storage.py`
- `synthesize_neural_voice.py`
- `synthesize_voice.ps1`
- `split_contact_sheet.py`
- `redesign_openers.py`
- `plantilla_infografia.png`

También se identificaron recursos relacionados con la generación de infografías verticales mediante Pillow, la división de hojas de contacto generadas por IA y la síntesis de voz mediante `edge_tts`.

La síntesis de voz ya contemplaba una voz colombiana, `es-CO-GonzaloNeural`, y el uso de FFmpeg para generar audio WAV.

El proyecto también maneja trabajos y datos en formato JSON, con una estructura de almacenamiento bajo `data/jobs`.

**Regla fundamental:** reutilizar el código existente. No reconstruir todo desde cero ni reemplazar módulos importantes sin inspeccionar su contenido y comprender cómo se relacionan.

Los módulos `pipeline.py`, `catalog.py` y `storage.py` deben conservarse, salvo que una modificación posterior resulte necesaria, esté justificada y se haga de forma compatible.

# 3. PRIMERA ETAPA: INTERFAZ GRÁFICA

Se preparó un primer paquete de la aplicación:

`video_factory_gui_mvp.zip`

El paquete añadió una interfaz gráfica basada en PySide6, con archivos como:

- `video_factory/gui/__init__.py`
- `video_factory/gui/__main__.py`
- `video_factory/gui/main_window.py`
- `requirements-gui.txt`
- `README_GUI.md`

La interfaz inicial contempla secciones para:

- Inicio.
- Crear trabajo.
- Trabajos.
- Configuración.

La ventana gráfica utiliza funciones del proyecto existente, entre ellas `create_job`, `list_ideas`, `render_job` y `run_job`, importadas desde `pipeline.py`, además de funciones de almacenamiento de `storage.py`.

El objetivo de esa primera etapa fue proporcionar una interfaz para crear trabajos, consultar su estado y ejecutar las operaciones que ya ofrece el pipeline.

**Estado confirmado por el usuario:** informó que instaló la primera versión y que la aplicación se ejecutó correctamente.

Esto confirma que la GUI básica llegó a funcionar, pero no significa que todas las operaciones de producción de video estén verificadas de extremo a extremo.

# 4. SEGUNDA ETAPA: BÚSQUEDA DE CLIPS

El usuario decidió continuar con la etapa 2 y definió expresamente estas condiciones:

- **Bancos de recursos:** Pexels y Pixabay.
- **Selección:** búsqueda y selección automáticas, con revisión manual antes del montaje.
- **Duración objetivo del video final:** 45 segundos.
- **Compatibilidad:** mantener los módulos existentes.
- **Configuración:** utilizar claves API propias y explicar cómo configurarlas.

## Flujo funcional acordado

La aplicación debe:

1. Tomar el tema del trabajo.
2. Buscar clips relevantes en Pexels y Pixabay.
3. Proponer una selección automática de resultados.
4. Priorizar, cuando los datos estén disponibles, los videos verticales o con proporciones adecuadas para un formato 9:16.
5. Permitir que el usuario revise los resultados y desmarque los que no quiera.
6. Esperar una aprobación explícita.
7. Descargar únicamente los clips aprobados.
8. Guardar los clips y un manifiesto con los metadatos y la procedencia de cada recurso.

El parche propuesto contempla hasta ocho sugerencias iniciales. Esa cifra es una decisión de implementación de la interfaz, no un requisito inamovible del proyecto.

La selección automática no debe significar descarga o publicación sin supervisión: la revisión humana antes de la descarga es una condición explícita.

## Recursos oficiales

Documentación de Pexels:

https://www.pexels.com/api/documentation/

Documentación de Pixabay:

https://pixabay.com/api/docs/

Ambos servicios ofrecen APIs para buscar recursos audiovisuales. Hay que respetar sus límites de uso y condiciones de licencia.

No debemos asumir que todos los clips pueden utilizarse de cualquier forma ni que todas las condiciones de atribución son idénticas.

El manifiesto debe conservar, en la medida en que la API proporcione estos datos, información como:

- Banco de origen.
- Identificador del recurso.
- URL del recurso original.
- Autor o creador.
- URL de la página del recurso.
- Duración.
- Dimensiones.
- Enlace de descarga.
- Datos de licencia o atribución disponibles.
- Ruta local del archivo descargado.

# 5. PARCHE PREPARADO PARA LA ETAPA 2

Se preparó un archivo ZIP con el nombre:

`video_factory_etapa2_patch.zip`

En la conversación se proporcionó el enlace:

sandbox:/mnt/data/video_factory_etapa2_patch.zip

El parche fue presentado como una actualización incremental que añade la funcionalidad de búsqueda y descarga de clips a la aplicación anterior.

Entre los archivos descritos para el parche se encuentran:

- `clips.py`: conexión con los bancos de clips, búsqueda y descarga.
- `gui/clips_panel.py`: interfaz para buscar, revisar y aprobar los resultados.
- `gui/main_window.py`: modificación para integrar la nueva pestaña.
- `.env.example`: plantilla para las claves API.
- `requirements-stage2.txt`: dependencias necesarias para la etapa 2.
- Un archivo de instrucciones para esta etapa.

La lista anterior describe los archivos que se anunciaron en el parche. **La otra sesión debe inspeccionar el ZIP real antes de modificar el proyecto o asumir que los archivos están instalados.**

## Ruta prevista de instalación

La primera ruta de proyecto que se manejó fue:

`D:\Adrian\Redes sociales\video_factory`

Las instrucciones dadas fueron extraer el ZIP en:

`D:\Adrian\Redes sociales`

La intención era que el contenido del parche se integrara en la carpeta `video_factory`, conservando los módulos originales.

Se indicó que podría ser necesario reemplazar `gui/main_window.py` para incorporar la nueva pestaña. Antes de volver a hacerlo, conviene verificar las copias y el estado actual de los archivos.

## Estado real de esta etapa

Todavía no hay confirmación del usuario de que:

- El parche se haya instalado correctamente.
- La pestaña de bancos de clips aparezca en la GUI.
- Las claves API estén configuradas.
- Pexels responda correctamente.
- Pixabay responda correctamente.
- Se hayan descargado clips.
- El manifiesto se haya generado correctamente.

Por tanto, la etapa 2 debe considerarse **preparada, pero pendiente de validación en el equipo del usuario**.

# 6. CONFIGURACIÓN DE LAS CLAVES API

Se indicó al usuario que necesita obtener una clave de cada servicio:

- Pexels: `PEXELS_API_KEY`
- Pixabay: `PIXABAY_API_KEY`

Las claves deben guardarse en un archivo `.env` en la carpeta raíz del proyecto, siguiendo el formato de `.env.example`.

Ejemplo de contenido, usando marcadores y no claves reales:

    PEXELS_API_KEY=TU_CLAVE_REAL_DE_PEXELS
    PIXABAY_API_KEY=TU_CLAVE_REAL_DE_PIXABAY

El archivo debe guardarse con el nombre exacto `.env`, sin añadir accidentalmente la extensión `.txt`.

No se deben incluir las claves en el código fuente ni compartirlas en mensajes de soporte.

También hay que verificar que el código realmente cargue las variables del archivo `.env`. La existencia del archivo, por sí sola, no garantiza que Python lo lea. Si se utiliza `python-dotenv`, debe estar instalado y su carga debe estar implementada en el código correspondiente.

No se ha confirmado todavía que el usuario haya completado este proceso.

# 7. DURACIÓN OBJETIVO: 45 SEGUNDOS

El usuario seleccionó expresamente una duración objetivo de 45 segundos.

Esto corresponde a la duración del video final, no necesariamente a la duración individual de cada clip.

En la etapa 2, el sistema busca y prepara recursos que posteriormente se usarán para el montaje.

En la etapa 3 habrá que implementar o conectar la lógica que permita:

- Seleccionar fragmentos relevantes.
- Calcular cuánto debe durar cada escena.
- Recortar los clips.
- Ajustar el encuadre a 9:16.
- Sincronizar las escenas con la narración.
- Ajustar el montaje para aproximarse a los 45 segundos.
- Resolver qué hacer cuando la narración o los recursos disponibles no encajan exactamente en ese tiempo.

No se debe afirmar que el video final ya se limita automáticamente a 45 segundos: eso queda pendiente del montaje y su validación.

# 8. PROBLEMA ACTUAL: ERROR DE ZONA HORARIA

Al ejecutar la aplicación, el usuario compartió una traza de error que termina así:

    ModuleNotFoundError: No module named 'tzdata'

    zoneinfo.ZoneInfoNotFoundError:
    'No time zone found with key America/Bogota'

La traza permite identificar la secuencia:

1. La GUI ejecuta una tarea para crear un trabajo.
2. Se llama a `create_job()` en `pipeline.py`.
3. `create_job()` invoca `now_iso()` en `storage.py`.
4. `now_iso()` utiliza:

       datetime.now(ZoneInfo("America/Bogota")).isoformat(timespec="seconds")

5. Python no encuentra los datos de la zona horaria `America/Bogota`.
6. Se produce la excepción y falla la creación del trabajo.

La traza mostró que el intérprete que estaba ejecutando esa operación provenía de:

`D:\Programs\Python\Python314\Lib\zoneinfo\_common.py`

Esto sugiere que se estaba utilizando Python 3.14, posiblemente el intérprete global. Hay que comprobarlo antes de concluir que la aplicación está utilizando el entorno virtual correcto.

## Solución recomendada que ya se indicó

Instalar `tzdata` en el mismo intérprete que ejecuta Video Factory:

    python -m pip install tzdata

Después verificar la zona horaria con:

    python -c "from zoneinfo import ZoneInfo; from datetime import datetime; print(datetime.now(ZoneInfo('America/Bogota')))"

Si funciona, debe mostrar la fecha y hora de Colombia.

## Verificaciones adicionales propuestas

Se pidió ejecutar:

    python -c "import sys; print(sys.executable)"
    python -m pip show tzdata

Estos comandos permiten comprobar qué intérprete se está utilizando y si ese entorno tiene instalado `tzdata`.

**Estado:** el usuario todavía no ha compartido el resultado de estas verificaciones. No sabemos si ya instaló el paquete ni si el error quedó resuelto.

# 9. CREACIÓN DEL ENTORNO VIRTUAL

El usuario preguntó cómo crear un entorno virtual.

Se explicó el procedimiento para Windows mediante PowerShell.

Primero, entrar a la carpeta:

    cd "D:\Adrian\Redes sociales\video_factory"

Comprobar Python:

    py --version

Crear el entorno virtual:

    py -m venv .venv

Activarlo:

    .\.venv\Scripts\Activate.ps1

La línea de PowerShell debería mostrar un prefijo como:

    (.venv) PS D:\Adrian\Redes sociales\video_factory>

Si PowerShell bloquea la activación, se indicó ejecutar:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Y después volver a activar el entorno.

Con el entorno activado, se propuso:

    python -m pip install --upgrade pip
    python -m pip install -r requirements-stage2.txt

Para iniciar la aplicación, se había indicado:

    cd "D:\Adrian\Redes sociales"
    python -m video_factory.gui

Estos comandos presuponen que la carpeta del proyecto y los archivos están organizados de esa forma y que `.venv` está dentro de la carpeta `video_factory`.

# 10. IMPORTANTE: HAY DOS RUTAS DISTINTAS EN EL HISTORIAL

La primera ruta de trabajo indicada fue:

`D:\Adrian\Redes sociales\video_factory`

Sin embargo, la traza de error más reciente muestra que el archivo que se estaba ejecutando está en:

`D:\Adrian\Redes sociales\Gui_Video_factory\video_factory_gui_mvp\video_factory\gui\main_window.py`

También aparecen:

`D:\Adrian\Redes sociales\Gui_Video_factory\video_factory_gui_mvp\video_factory\pipeline.py`

y:

`D:\Adrian\Redes sociales\Gui_Video_factory\video_factory_gui_mvp\video_factory\storage.py`

Esto es importante. Puede tratarse de una copia diferente del proyecto, de la carpeta donde se extrajo el primer ZIP o de una instalación anterior.

**La próxima sesión debe confirmar cuál de las carpetas contiene la versión que el usuario ejecuta realmente antes de indicarle dónde instalar el parche o crear `.venv`.**

No se debe asumir que las instrucciones dadas para `D:\Adrian\Redes sociales\video_factory` se aplican automáticamente a la copia ubicada en `Gui_Video_factory\video_factory_gui_mvp`.

# 11. PRÓXIMOS PASOS, EN ORDEN DE PRIORIDAD

## Prioridad 1: resolver el entorno Python

1. Confirmar cuál es la carpeta activa del proyecto.
2. Abrir PowerShell en esa carpeta.
3. Ejecutar `py --version`.
4. Comprobar si existe `.venv`.
5. Si no existe, crear el entorno virtual en la carpeta correcta.
6. Activarlo.
7. Instalar las dependencias de la GUI y de la etapa 2.
8. Instalar `tzdata`.
9. Verificar que `sys.executable` apunte al intérprete esperado.
10. Probar la zona horaria `America/Bogota`.

No hay que crear varios entornos virtuales innecesarios. Primero debe identificarse el entorno que utiliza la aplicación.

## Prioridad 2: comprobar el parche

1. Verificar que `video_factory_etapa2_patch.zip` esté disponible.
2. Inspeccionar su estructura y contenido.
3. Comparar sus archivos con la copia real del proyecto.
4. Evitar sobrescribir archivos sin respaldo.
5. Instalar las dependencias.
6. Verificar que la GUI importe correctamente.
7. Confirmar que aparezca la pestaña de bancos de clips.

## Prioridad 3: configurar las APIs

1. Obtener una clave válida de Pexels.
2. Obtener una clave válida de Pixabay.
3. Crear el archivo `.env`.
4. Verificar que el código lea ambas variables.
5. Probar las dos APIs por separado.
6. Gestionar errores de autenticación, límites de solicitudes y ausencia de resultados.

## Prioridad 4: probar la selección y descarga

1. Crear un trabajo.
2. Buscar clips sobre un tema sencillo.
3. Confirmar que se reciban resultados de ambos bancos.
4. Revisar las dimensiones y duración disponibles.
5. Comprobar que el usuario pueda desmarcar sugerencias.
6. Verificar que la descarga solo ocurra después de la aprobación.
7. Confirmar que los archivos y el manifiesto se guarden correctamente.
8. Verificar los metadatos de procedencia y las condiciones de uso.

## Prioridad 5: desarrollar la etapa 3

Una vez estable y probada la etapa 2, continuar con el montaje automático:

- Selección de fragmentos.
- Recorte y encuadre vertical 9:16.
- Narración sintética.
- Subtítulos.
- Sincronización entre audio e imágenes.
- Montaje mediante FFmpeg.
- Duración objetivo de 45 segundos.
- Exportación y validación del video final.

Debe reutilizarse el pipeline original en lugar de crear un sistema paralelo innecesario.

# 12. REGLAS PARA CONTINUAR EL DESARROLLO

La próxima sesión debe respetar estas condiciones:

1. No reconstruir todo el proyecto desde cero.
2. No eliminar ni sustituir módulos existentes sin inspeccionarlos.
3. No inventar la estructura real de los archivos: verificarla antes de modificar.
4. No confundir el ZIP de la GUI inicial con el parche de la etapa 2.
5. No asumir que una función está terminada solo porque existe un archivo para ella.
6. Probar las operaciones en el entorno disponible y distinguir las pruebas realizadas de las que aún debe ejecutar el usuario.
7. No solicitar ni mostrar las claves API reales.
8. Mantener la revisión humana antes de la descarga de los clips.
9. Registrar la procedencia de los recursos y respetar sus condiciones de licencia.
10. No pasar a la etapa 3 hasta que la búsqueda, selección, descarga y almacenamiento de metadatos estén funcionando de forma verificable.

# 13. MENSAJE PARA CONTINUAR EN LA NUEVA SESIÓN

Quiero continuar el desarrollo de Video Factory a partir de este contexto.

La primera versión de la GUI basada en PySide6 llegó a funcionar. Se preparó un parche para la etapa 2, que debe añadir búsqueda en Pexels y Pixabay, selección automática con revisión humana, descarga aprobada y un manifiesto de metadatos. El video final tendrá una duración objetivo de 45 segundos.

Ahora mismo necesito resolver el problema del entorno Python y de `tzdata`, y después verificar que la etapa 2 esté instalada en la carpeta correcta.

La primera ruta indicada fue `D:\Adrian\Redes sociales\video_factory`, pero la traza más reciente muestra que la aplicación se ejecuta desde `D:\Adrian\Redes sociales\Gui_Video_factory\video_factory_gui_mvp\video_factory`. Antes de dar instrucciones de instalación, ayúdame a identificar cuál de las dos carpetas es la versión activa.

Trabaja de forma incremental, inspecciona los archivos reales antes de modificarlos y conserva los módulos originales. No des por hecho que la etapa 2 ya está probada: todavía falta confirmar que las APIs, las claves, la selección, la descarga y el manifiesto funcionen en mi equipo.

Cuando eso esté estable, avanzaremos a la etapa 3 para automatizar el montaje vertical, la voz, los subtítulos y la exportación final de 45 segundos.
