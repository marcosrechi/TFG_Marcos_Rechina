import sys
import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CARPETA_A_MONITOREAR = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Pruebas Monitoreo"
SCRIPT_PROCESADOR = r""

class PDFHandler(FileSystemEventHandler):


    def on_created(self, event):
        """Se ejecuta cuando se crea un archivo en la carpeta."""
        if not event.is_directory:
            self.procesar_comun(event.src_path)
        
        '''
        filename = event.src_path
        if filename.lower().endswith(".pdf"):
            print(f"[DETECTADO] Nuevo PDF: {filename}")
            
            # Esperamos a que el archivo sea totalmente accesible
            if self.esperar_escritura_archivo(filename):
                self.ejecutar_procesamiento(filename)
            else:
                print(f"[ERROR] No se pudo acceder a {filename} después de varios intentos.")
        '''
    
    def on_moved(self, event):
        if not event.is_directory:
            self.procesar_comun(event.dest_path)


    def procesar_comun(self, ruta):
        if ruta.lower().endswith(".pdf"):
            print(f"Nuevo PDF detectado en: {ruta}")
            if self.esperar_escritura_archivo(ruta):
                print(f"PDF liberado")
        
    
    def esperar_escritura_archivo(self, filepath, retries=10, delay=1):
        """
        Intenta abrir el archivo en modo append para verificar que 
        ningún otro proceso lo tiene bloqueado (escribiendo).
        """
        for i in range(retries):
            try:
                # Si podemos abrirlo en 'append', significa que está liberado
                with open(filepath, 'ab'):
                    pass
                return True
            except IOError:
                # El archivo está bloqueado o siendo escrito
                time.sleep(delay)
        return False

    '''
    def ejecutar_procesamiento(self, filepath):
        """Llama al script externo procesar_pdf.py"""
        print(f"[PROCESANDO] Enviando a {SCRIPT_PROCESADOR}...")
        try:
            # Llamada al script existente pasando la ruta como argumento
            resultado = subprocess.run(
                ["python", SCRIPT_PROCESADOR, filepath], 
                capture_output=True, 
                text=True
            )
            if resultado.returncode == 0:
                print(f"[EXITO] Resultado: {resultado.stdout.strip()}")
            else:
                print(f"[FALLO] Error en script: {resultado.stderr}")
        except Exception as e:
            print(f"[ERROR] Al ejecutar script: {e}")

    '''

if __name__ == "__main__":
    if not os.path.isdir(CARPETA_A_MONITOREAR):
        print("La carpeta especificada no existe.")
        sys.exit(1)

    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, CARPETA_A_MONITOREAR, recursive=False)
    observer.start()
    
    print(f"Monitoreando carpeta: {CARPETA_A_MONITOREAR}")
    print("Presiona Ctrl+C para detener.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()