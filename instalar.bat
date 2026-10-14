@echo off
setlocal
cd /d "%~dp0"
echo ==============================================
echo  Instalacion de Video Factory
echo ==============================================

where py >nul 2>nul
if errorlevel 1 (
  echo.
  echo [ERROR] No se encontro Python. Instala Python 3.11 o superior desde https://www.python.org/downloads/
  echo         y marca la casilla "Add python.exe to PATH". Luego ejecuta de nuevo este archivo.
  pause
  exit /b 1
)

if not exist "video_factory\.venv\Scripts\python.exe" (
  echo.
  echo [1/5] Creando el entorno virtual...
  py -3 -m venv video_factory\.venv
  if errorlevel 1 goto :fallo
) else (
  echo [1/5] Entorno virtual ya existe.
)

echo.
echo [2/5] Instalando la interfaz (PySide6)...
video_factory\.venv\Scripts\python.exe -m pip install --upgrade pip
video_factory\.venv\Scripts\python.exe -m pip install -r video_factory\requirements-gui.txt
if errorlevel 1 goto :fallo

echo.
echo [3/5] Instalando la voz neuronal (edge-tts)...
video_factory\.venv\Scripts\python.exe -m pip install --target data\tts-packages edge-tts
if errorlevel 1 goto :fallo

echo.
echo [4/5] Buscando FFmpeg...
where ffmpeg >nul 2>nul
if errorlevel 1 (
  dir /s /b "%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*ffmpeg.exe" 2>nul | findstr /i "ffmpeg.exe" >nul
  if errorlevel 1 (
    echo FFmpeg no esta instalado. Instalando con winget...
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
  ) else (
    echo FFmpeg ya esta instalado por winget.
  )
) else (
  echo FFmpeg encontrado en el PATH.
)

echo.
echo [5/5] Preparando configuracion y acceso directo...
if not exist "video_factory\.env" (
  copy "video_factory\.env.example" "video_factory\.env" >nul
  echo Se creo video_factory\.env : abrelo con el Bloc de notas y pon tus claves de Pexels y Pixabay.
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=(Get-Location).Path; $s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Video Factory.lnk'); $s.TargetPath=$p+'\video_factory\.venv\Scripts\pythonw.exe'; $s.Arguments='-m video_factory.gui'; $s.WorkingDirectory=$p; $s.IconLocation=$p+'\assets\video_factory.ico'; $s.Save()"

echo.
echo ==============================================
echo  Listo. Abre "Video Factory" desde el Escritorio.
echo  Si acabas de instalar FFmpeg, cierra y vuelve a abrir la app.
echo ==============================================
if "%1"=="/silencioso" exit /b 0
pause
exit /b 0

:fallo
echo.
echo [ERROR] Algo fallo en la instalacion. Revisa los mensajes anteriores.
if not "%1"=="/silencioso" pause
exit /b 1
