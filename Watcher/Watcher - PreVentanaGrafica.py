import sys
import time
import os
import csv
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from CasillasMarcadasModif import Extraer_Numero_Matricula # type: ignore

CARPETA_A_MONITOREAR = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Pruebas Monitoreo"
RUTA_BASE_DE_DATOS = r"C:\Users\marco\Documents\GitHub\TFG_Marcos_Rechina\BaseDeDatosAlumnos.json"
SCRIPT_PROCESADOR = r""
RUTA_FICHERO_TXT = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Ficheros\Fichero_TXT.txt"
RUTA_FICHERO_EXCEL = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Ficheros\Fichero_EXCEL.xlsx"
RUTA_FICHERO_CSV = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Ficheros\Fichero_CSV.csv"

DICCIONARIO_JSON = {}
CORREO_ORIGEN = "pruebastfgmarcosrechina@gmail.com"
CONTRASEÑA_ORIGEN = "jjao hbsb hvee jpqh"

def Procesar_Nuevo_PDF(ruta):
    if ruta.lower().endswith(".pdf"):
        print(f"Nuevo PDF detectado en: {ruta}")
        if not Esperar_Liberacion_Archivo(ruta):
            return
        
        try:
            numero_matricula = Extraer_Numero_Matricula(ruta)
            # print(f"Valor visual:  {numero_matricula}")          # Lo que ves normalmente
            # print(f"Tipo Python:   {type(numero_matricula)}")    # Si es str, int, float...
            # print(f"Valor REAL:    {repr(numero_matricula)}")    # <--- ¡LA CLAVE! Muestra comillas y espacios
            Gestion_Numero_Matricula(numero_matricula)
            print(f"PDF liberado con numero de matricula {numero_matricula}")
        
        except Exception as e:
            print(f"[ERROR] {e}")

def Esperar_Liberacion_Archivo(ruta, intentos=10, delay=1):
        """
        Intenta abrir el archivo en modo append para verificar que 
        ningún otro proceso lo tiene bloqueado (escribiendo).
        """
        for i in range(intentos):
            try:
                # Si podemos abrirlo en 'append', significa que está liberado
                with open(ruta, 'ab') as doc:
                    pass
                return True
            except IOError:
                # El archivo está bloqueado o siendo escrito
                time.sleep(delay)
        return False

def Gestion_Numero_Matricula(numero_matricula):
    if ("X" or "x") in numero_matricula:
        print(f"Error en la obtención del número de matrícula")
        return None

    datos_alumno = Comprobar_Informacion(numero_matricula)
    if datos_alumno is None:
        return None
    
    print(f"El correo del alumno con el numero de matricula {numero_matricula} es: {datos_alumno["Correo"]}")
    Mandar_Correo(numero_matricula, datos_alumno)
    Escribir_CSV(numero_matricula, datos_alumno)
    # Escribir_Txt()
    # Escribir_Excel()
    
    return

def Escribir_CSV(numero_matricula, datos_alumno):

    global RUTA_FICHERO_CSV

    # ["Numero Matricula", "Nombre", "Hora Entrega", "Nota", ]
    hora_entrega = time.strftime("%d/%m/%Y %H:%M", time.localtime())

    datos_csv = [numero_matricula, datos_alumno["Nombre"], hora_entrega, "S/C"]

    try:
        with open(RUTA_FICHERO_CSV, mode='a', newline='', encoding='utf-8-sig') as archivo:
            # El modo a añade lo que escribas al final del archivo ya existente

            escritor = csv.writer(archivo, delimiter=';')
            escritor.writerow(datos_csv)
        
        # print("Línea añadida.") # Opcional para debug
    except PermissionError:
        print("Error: No se pudo escribir. El archivo está bloqueado.")

    return

def Escribir_Txt():
    pass

def Escribir_Excel():
    pass

def Mandar_Correo(numero_matricula, datos_alumno):
    # Configuración del servidor y credenciales
    # smtp_server = "smtp.office365.com"                # Para correo basado en Outlook
    smtp_server = "smtp.gmail.com"                      # Para correo basado en Gmail
    smtp_port = 587
    global CORREO_ORIGEN, CONTRASEÑA_ORIGEN
    
    asunto = "Entrega de examen confirmada"
    cuerpo = f"Se confirma mediante el envío de este correo que el alumn@ {datos_alumno["Nombre"]} con matrícula {numero_matricula} ha realizado el examen de INFORMÁTICA"

    # Crear el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = CORREO_ORIGEN
    msg['To'] = datos_alumno["Correo"]
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        # Conexión al servidor
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Cifrado obligatorio para Office 365
        
        # Inicio de sesión
        server.login(CORREO_ORIGEN, CONTRASEÑA_ORIGEN)
        
        # Envío
        server.send_message(msg)
        print("¡Correo enviado con éxito!")
    
    except Exception as e:
        print(f"ERROR: {e}")
    
    finally:
        server.quit

    return

def Comprobar_Informacion(numero_matricula):
    datos_alumno = DICCIONARIO_JSON.get(numero_matricula)
    if datos_alumno is None:
        # print(f"No se ha encontrado alumno con numero de matricula: {numero_matricula}")
        return None
    else:
        # print(f"Encontrado alumno con numero de matricula: {numero_matricula}")
        return datos_alumno
    pass

def Crear_Fichero_CSV():

    global RUTA_FICHERO_CSV

    encabezados = ["Numero Matricula", "Nombre", "Hora Entrega", "Nota", ]

    try:
        with open(RUTA_FICHERO_CSV, mode='w', newline='', encoding='utf-8-sig') as archivo:
            # El modo w crea un archivo si no lo hay, y si lo hay lo sobreescribe por completo
            
            escritor = csv.writer(archivo, delimiter=';') # Usamos ';' para mejor compatibilidad con Excel en español
            escritor.writerow(encabezados)

        print(f"Archivo '{RUTA_FICHERO_CSV}' inicializado correctamente.")
    except PermissionError:
        print("Error: No se pudo inicializar. Cierra el archivo si lo tienes abierto en Excel.")


def Cargar_Datos_JSON():
    global DICCIONARIO_JSON
    if os.path.exists(RUTA_BASE_DE_DATOS):
        try:
            with open(RUTA_BASE_DE_DATOS, "r", encoding="utf-8-sig") as f:
                DICCIONARIO_JSON = json.load(f)

        except Exception as e:
            print(f"Error leyendo el json: {e}")
            return None

    else:
        print(F"No se encontro la base de datos: {RUTA_BASE_DE_DATOS}")
        return None

class PDFHandler(FileSystemEventHandler):

    def on_created(self, event):
        """Se ejecuta cuando se crea un archivo en la carpeta."""
        if not event.is_directory:
            Procesar_Nuevo_PDF(event.src_path)
        
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
            Procesar_Nuevo_PDF(event.dest_path)

    '''

    PARA EJECUTAR EL SCRIPT DE PYHTON EN VEZ DE IMPORTARLO

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

    Cargar_Datos_JSON()
    Crear_Fichero_CSV()

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










# ---------------------------------------------------------------------------------------------------------
# PARA HACERLO UN SERVICIO CON EL ICONO EN EL SITIO DE ABAJO DONDE EL RELOJ COMO EN STEAM, TEAMS ETC ETC
# ---------------------------------------------------------------------------------------------------------

# import os
# import sys
# import time
# import threading
# import subprocess
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# # Librerías para la bandeja del sistema
# import pystray
# from PIL import Image, ImageDraw

# # --- CONFIGURACIÓN ---
# CARPETA_A_MONITOREAR = r"C:\Ruta\A\Tu\Carpeta"  # <--- CAMBIA ESTO
# SCRIPT_PROCESADOR = "procesar_pdf.py"

# # --- LÓGICA DEL VIGILANTE (WATCHDOG) ---
# class PDFHandler(FileSystemEventHandler):
#     def _procesar_comun(self, filename):
#         if filename.lower().endswith(".pdf"):
#             # Opcional: Mostrar una notificación de Windows aquí si quisieras
#             if self.esperar_escritura_archivo(filename):
#                 self.ejecutar_procesamiento(filename)

#     def on_created(self, event):
#         if not event.is_directory:
#             self._procesar_comun(event.src_path)

#     def on_moved(self, event):
#         if not event.is_directory:
#             self._procesar_comun(event.dest_path)

#     def esperar_escritura_archivo(self, filepath, retries=10, delay=1):
#         for i in range(retries):
#             try:
#                 with open(filepath, 'ab'):
#                     pass
#                 return True
#             except IOError:
#                 time.sleep(delay)
#         return False

#     def ejecutar_procesamiento(self, filepath):
#         # Usamos subprocess con creación de ventana oculta para que NO salte una terminal negra
#         startupinfo = subprocess.STARTUPINFO()
#         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
#         try:
#             subprocess.run(
#                 ["python", SCRIPT_PROCESADOR, filepath],
#                 capture_output=True,
#                 text=True,
#                 startupinfo=startupinfo # Esto oculta la terminal del subproceso
#             )
#         except Exception:
#             pass 

# # --- LÓGICA DE LA BANDEJA DEL SISTEMA (TRAY) ---

# def crear_icono():
#     """Genera un icono simple (cuadrado bicolor) en memoria."""
#     width = 64
#     height = 64
#     image = Image.new('RGB', (width, height), color=(255, 255, 255))
#     dc = ImageDraw.Draw(image)
#     dc.rectangle((0, height // 2, width, height), fill=(0, 120, 215)) # Azul
#     dc.rectangle((0, 0, width, height // 2), fill=(255, 200, 0))    # Amarillo
#     return image

# def salir_accion(icon, item):
#     """Se ejecuta al dar Clic Derecho -> Salir"""
#     icon.stop() # Detiene el icono
#     observer.stop() # Detiene al vigilante
#     sys.exit(0)

# def iniciar_vigilancia():
#     global observer
#     if not os.path.isdir(CARPETA_A_MONITOREAR):
#         # Si la carpeta no existe, no podemos arrancar. 
#         # En una app real, aquí mostrarías un error gráfico.
#         return

#     event_handler = PDFHandler()
#     observer = Observer()
#     observer.schedule(event_handler, CARPETA_A_MONITOREAR, recursive=False)
#     observer.start()

# # --- EJECUCIÓN PRINCIPAL ---
# if __name__ == "__main__":
#     # 1. Iniciamos el vigilante (Watchdog)
#     iniciar_vigilancia()

#     # 2. Creamos el icono y el menú
#     image = crear_icono()
#     menu = pystray.Menu(
#         pystray.MenuItem('Monitoreando PDFs...', lambda icon, item: None, enabled=False), # Texto informativo
#         pystray.Menu.SEPARATOR,
#         pystray.MenuItem('Salir', salir_accion) # Botón de salir
#     )

#     icon = pystray.Icon("MonitorPDF", image, "Vigilante de PDFs", menu)
    
#     # 3. Ejecutamos el icono (Esto bloquea el script hasta que le des a Salir)
#     icon.run()
    
#     # Cuando icon.run() termina (porque diste a Salir), nos aseguramos de cerrar el hilo del observer
#     if 'observer' in globals() and observer.is_alive():
#         observer.join()




'''

PARA EJECUTAR EL SCRIPT DE PYHTON EN VEZ DE IMPORTARLO

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