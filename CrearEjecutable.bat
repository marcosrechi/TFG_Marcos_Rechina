@echo off
setlocal

:: --- CONFIGURACIÓN ---
set SCRIPT_PRINCIPAL=WatcherModif.py
set NOMBRE_EJECUTABLE=GestorExamenes
:: ---------------------

echo [1/4] Borrando versiones anteriores para una compilacion limpia...
:: Borramos la carpeta dist entera para que no haya archivos viejos
if exist dist rmdir /s /q dist
:: Borramos la carpeta build (temporales de PyInstaller)
if exist build rmdir /s /q build
:: Borramos el archivo .spec (configuracion temporal)
if exist %NOMBRE_EJECUTABLE%.spec del /f /q %NOMBRE_EJECUTABLE%.spec

echo [2/4] Verificando PyInstaller...
pip install pyinstaller --quiet

echo [3/4] Creando el ejecutable (esto puede tardar)...
:: --noconfirm: no pregunta si queremos sobrescribir
:: --onefile: todo en un solo .exe
:: --windowed: no abre consola negra al ejecutar (quitar si es app de consola)
pyinstaller --noconfirm --onefile --windowed --name %NOMBRE_EJECUTABLE% %SCRIPT_PRINCIPAL%

echo [4/4] Limpiando residuos temporales...
:: Borramos build y el .spec, pero DEJAMOS la carpeta 'dist' intacta
if exist build rmdir /s /q build
if exist %NOMBRE_EJECUTABLE%.spec del /f /q %NOMBRE_EJECUTABLE%.spec

echo.
echo ======================================================
echo PROCESO COMPLETADO CON EXITO
echo Tu ejecutable limpio esta en: \dist\%NOMBRE_EJECUTABLE%.exe
echo ======================================================
pause