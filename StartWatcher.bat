@echo off

:: Cambia el directorio de trabajo al lugar donde está el batch
cd /d "%~dp0"

:: Ejecuta el script usando pythonw para que sea silencioso (sin consola)
start "" pythonw.exe "WatcherModif.py"

:: Cierra la ventana del terminal del batch inmediatamente
exit