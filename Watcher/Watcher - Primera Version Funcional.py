# Para parar el programa antes de tiempo
import sys

# Para trabajar con hilos
import threading

# Para el icono en la zona de procesos / servicios
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# Para poder poner en cola los diferentes PDFs y que no se pisen unos a otros
from queue import Queue

# Para el tiempo y el delay
import time

# Para trabajar con las rutas
import os

# Para trabajar con archivos csv
import csv

# Para trabajar con archivos json
import json

# Para la ventana gráfica
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Para trabajar con watchdogs
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Para enviar emails
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# El script encargado de obtener el numero de matrícula del PDF
from CasillasMarcadasModif import Extraer_Numero_Matricula # type: ignore

# Ruta del archivo JSON (HAY QUE CAMBIAR A QUE SEAN RUTAS RELATIVAS)
RUTA_BASE_DE_DATOS = r"C:\Users\marco\Documents\GitHub\TFG_Marcos_Rechina\BaseDeDatosAlumnos.json"
SCRIPT_PROCESADOR = r""

# Variables globales usadas en el código
RUTA_FICHERO_CSV = None
DICCIONARIO_JSON = None

# Datos de correo origen
CORREO_ORIGEN = "pruebastfgmarcosrechina@gmail.com"
CONTRASEÑA_ORIGEN = "jjao hbsb hvee jpqh"

# Función encargada de procesar cada nuevo PDF
def procesar_nuevo_pdf(ruta, callback_status):

    # Si el documento detectado es un PDF
    if ruta.lower().endswith(".pdf"):

        # Guarda la ruta del PDF
        nombre_archivo = os.path.basename(ruta)

        # La función callback_status sirve para cambiar el texto escrito en la ventana gráfica

        callback_status(f"Nuevo PDF: {nombre_archivo}")

        # Si el archivo no está liberado, no se continua con la función
        if not esperar_liberacion_archivo(ruta):
            return
        
        try:
            callback_status(f"Leyendo número de matrícula {nombre_archivo}...")

            # Se obtiene el número de matrícula con la función del otro script
            numero_matricula = Extraer_Numero_Matricula(ruta)

            # Comprueba que el número de matrícula sea válildo
            if "x" in numero_matricula.lower():
                print(f"Error en la obtención del número de matrícula")
                return None
            
            # Obtiene la información del alumno con el número de matrícula
            callback_status(f"Comprobando informacion del alumno con matrícula {numero_matricula}...")
            datos_alumno = comprobar_informacion(numero_matricula)
            if datos_alumno is None:
                return None
            
            # Escribe el correo que funciona como justificante
            callback_status(f"Mandando justificante por correo ...")
            mandar_correo(numero_matricula, datos_alumno)

            # Se actualiza el fichero con los datos del alumno detectado
            callback_status(f"Actualizando fichero ...")
            escribir_csv(numero_matricula, datos_alumno)

            # Modifica el texto para la espera de un nuevo PDF
            callback_status(f"Esperando nuevo PDF ...")
        
        except Exception as e:
            print(f"[ERROR] {e}")

# Detecta si el archivo está en uso o está liberado
def esperar_liberacion_archivo(ruta, intentos=10, delay=1):

    # Lo abrimos en modo "append" para verificarlo
    # Hace varios intentos para ver si está liberado antes de rendirse
    for i in range(intentos):
        try:
            # Si podemos abrirlo en 'append', significa que está liberado - DEVOLVEMOS UN TRUE
            with open(ruta, 'ab') as doc:
                pass
            return True
        
        # El archivo está bloqueado o siendo escrito
        except IOError:
            # Esperamos un tiempo antes del siguiente intento
            time.sleep(delay)
    
    # Si podemos abrirlo en 'append', significa que está liberado - DEVOLVEMOS UN FALSE
    return False

# Función encargada de actualizar el fichero con los datos del alumno reconocido
def escribir_csv(numero_matricula, datos_alumno):

    global RUTA_FICHERO_CSV

    # Para guardar la hora de entrega
    hora_entrega = time.strftime("%d/%m/%Y %H:%M", time.localtime())

    # ["Numero Matricula", "Nombre", "Hora Entrega", "Nota", "Ruta del examen"]
    datos_csv = [numero_matricula, datos_alumno["Nombre"], hora_entrega, "S/C", "Mejora por poner"]

    # Escribimos en el fichero en modo "append" para no borrar lo anterior
    try:
        with open(RUTA_FICHERO_CSV, mode='a', newline='', encoding='utf-8-sig') as archivo:
            # El modo a añade lo que escribas al final del archivo ya existente

            escritor = csv.writer(archivo, delimiter=';')
            escritor.writerow(datos_csv)

    except PermissionError:
        print("Error: No se pudo escribir. El archivo está bloqueado.")

    return

def mandar_correo(numero_matricula, datos_alumno):

    # Configuración del servidor de correo y las correspondientes credenciales
    # smtp_server = "smtp.office365.com"                # Para correo basado en Outlook
    smtp_server = "smtp.gmail.com"                      # Para correo basado en Gmail
    smtp_port = 587
    global CORREO_ORIGEN, CONTRASEÑA_ORIGEN
    
    # Creamos el mensaje a enviar
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
        
        # Envío del mensaje
        server.send_message(msg)
        print("¡Correo enviado con éxito!")
    
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Para asegurarse que se cierra el servidor del correo
    finally:
        server.quit

    return

# Busca el número de matrícula en la base de datos y obtiene los datos del alumno
def comprobar_informacion(numero_matricula):
    datos_alumno = DICCIONARIO_JSON.get(numero_matricula)
    if datos_alumno is None:
        # print(f"No se ha encontrado alumno con numero de matricula: {numero_matricula}")
        return None
    else:
        return datos_alumno

# Clase para crear el fichero (OBSOLETA)
def crear_fichero_csv():

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


def cargar_datos_json():

    if getattr(sys, 'frozen', False):
        # Si es el .exe, busca la carpeta donde reside el .exe
        RUTA_CARPETA_APP = os.path.dirname(sys.executable)
    else:
        # Si es el .py, busca la carpeta del script
        RUTA_CARPETA_APP = os.path.dirname(os.path.abspath(__file__))

    ruta_base_de_datos = os.path.join(RUTA_CARPETA_APP, "BaseDeDatosAlumnos.json")

    global DICCIONARIO_JSON
    if os.path.exists(ruta_base_de_datos):
        try:
            with open(ruta_base_de_datos, "r", encoding="utf-8-sig") as f:
                DICCIONARIO_JSON = json.load(f)

        except Exception as e:
            print(f"Error leyendo el json: {e}")

    else:
        print(F"No se encontro la base de datos: {ruta_base_de_datos}")


    # global DICCIONARIO_JSON
    # if os.path.exists(RUTA_BASE_DE_DATOS):
    #     try:
    #         with open(RUTA_BASE_DE_DATOS, "r", encoding="utf-8-sig") as f:
    #             DICCIONARIO_JSON = json.load(f)

    #     except Exception as e:
    #         print(f"Error leyendo el json: {e}")

    # else:
    #     print(F"No se encontro la base de datos: {RUTA_BASE_DE_DATOS}")

# Clase encargada de la detección de nuevos documentos
class ProcesadorPDF(FileSystemEventHandler):

    # Cuando se crea esta clase se llama a esta función
    def __init__(self, cola):
        
        # Se pasa la cola de documentos para poder añadir documentos a esta
        self.cola = cola

    # Cuando el documento ha sido creado desde cero
    def on_created(self, event):
        
        # Si es un PDF lo pone en la cola
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            self.cola.put(event.src_path)
        

    # Cuando el documento ha sido movido desde otra carpeta
    def on_moved(self, event):

        # Si es un PDF lo pone en la cola
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            self.cola.put(event.src_path)

# Clase encargada de la ventana gráfica y del icono mostrado en la barra de tareas
class AppMonitor:

    # Función que se ejecuta al crear el Monitor
    def __init__(self, root):

        # Crear la ventana con las dimensiones y el título
        self.root = root
        self.root.title("Configuración de Monitor")
        self.root.geometry("700x300")
        
        # Variables (String variables a tiempo real) para guardar las rutas
        self.ruta_monitoreo = tk.StringVar()
        self.ruta_csv = tk.StringVar()

        # Ventana de selección de carpetas
        tk.Label(root, text="Rutas de monitoreo y creación de fichero", font=("Arial", 12, "bold")).pack(pady=10) # Para añadir texto

        # Entrada 1: Carpeta a Monitorizar
        frame1 = tk.Frame(root)
        frame1.pack(pady=10, padx=20, fill='x')
        tk.Label(frame1, text="Carpeta a vigilar:").pack(side='left')
        tk.Entry(frame1, textvariable=self.ruta_monitoreo, width=40).pack(side='left', padx=5) # Esta sería la variable donde se guardará la ruta
        tk.Button(frame1, text="Examinar", command=self.seleccionar_carpeta_monitoreo).pack(side='left') # Para abrir el explorador de archivos cuando cliques el botón

        # Campo 2: Carpeta para el CSV
        frame2 = tk.Frame(root)
        frame2.pack(pady=10, padx=20, fill='x')
        tk.Label(frame2, text="Donde guardar CSV:").pack(side='left')
        tk.Entry(frame2, textvariable=self.ruta_csv, width=40).pack(side='left', padx=5) # Esta sería la variable donde se guardará la ruta
        tk.Button(frame2, text="Examinar", command=self.seleccionar_carpeta_csv).pack(side='left') # Para abrir el explorador de archivos cuando cliques el botón

        # Botón para iniciar el monitoreo
        self.btn_iniciar = ttk.Button(root, text="Iniciar Monitoreo", command=self.validar_e_iniciar) # Cuando pulses el botón se comprobarán las rutas elegidas
        self.btn_iniciar.pack(pady=20)

    # Para abrir el explorador de archivos
    def seleccionar_carpeta_monitoreo(self):
        ruta = filedialog.askdirectory(title="Selecciona la carpeta para vigilar PDFs")
        if ruta:
            self.ruta_monitoreo.set(ruta) # Cuando se selecciona una carpeta se actualiza la variable mostrada en el display

    # Para abrir el explorador de archivos
    def seleccionar_carpeta_csv(self):

        # Estas son las extensiones permitidas para el fichero (por ahora solo csv)
        extensiones_guardado = [("Archivo CSV", "*.csv"), ("Todos los documentos", "*.*")]

        ruta = filedialog.asksaveasfilename(
            title = "¿Dónde quieres guardar el fichero?",
            defaultextension = ".csv",
            filetypes = extensiones_guardado,
            initialfile = "Fichero_Alumnos.csv") # Nombre sugerido para el fichero

        if ruta:
            self.ruta_csv.set(ruta) # Cuando se selecciona una ruta se actualiza la variable mostrada en el display

    # Comprobar si las rutas elegidas existen
    def validar_e_iniciar(self):

        # Si las rutas elegidas no existen, salta un mensaje de aviso y no deja continuar
        if not os.path.isdir(self.ruta_monitoreo.get()) or not os.path.isdir(os.path.dirname(self.ruta_csv.get())):
            messagebox.showwarning("Datos incorrectos", "No se han encontrado carpetas con esos nombres")
            return

        # Una vez validados, limpiamos la ventana y creamos la nueva
        self.preparar_interfaz_monitoreo()

        # Después lanzamos la función encargada de verdad del monitoreo de la carpeta
        self.iniciar_logica_tras_configuracion()

    # Limpiar la ventana y crear la nueva
    def preparar_interfaz_monitoreo(self):
        
        # Limpia todos los botones y textos actuales
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Aquí construimos la ventana "Monitorizando..."
        tk.Label(self.root, text="Monitor Activo", font=("Arial", 12, "bold"), fg="green").pack(pady=10)
        self.status_var = tk.StringVar(value="Esperando archivos...")
        tk.Label(self.root, textvariable=self.status_var, font=("Arial", 10), fg="blue").pack(pady=20) # Texto variable según el estado
        ttk.Button(self.root, text="Detener y Salir", command=self.parar_monitor).pack(pady=10) # Botón para salir del monitoreo


    def iniciar_logica_tras_configuracion(self):
        """Aquí arrancamos el Watchdog y la Cola con las rutas elegidas"""
        # Actualizamos las globales y locales
        carpeta_monitoreo = self.ruta_monitoreo.get()

        global RUTA_FICHERO_CSV
        RUTA_FICHERO_CSV = self.ruta_csv.get()

        # Abro el fichero, borro todo lo existente y escribo los encabezados del fichero 
        try:
            with open(RUTA_FICHERO_CSV, mode='w', newline='', encoding='utf-8-sig') as archivo:
                # El modo w crea un archivo si no lo hay, y si lo hay lo sobreescribe por completo

                encabezados_fichero = ["Numero Matricula", "Nombre", "Hora Entrega", "Nota", "Ruta del examen"]
                escritor = csv.writer(archivo, delimiter=';') # Usamos ';' para mejor compatibilidad con Excel en español
                escritor.writerow(encabezados_fichero)

        except PermissionError:
            print("Error: No se pudo inicializar. Cierra el archivo si lo tienes abierto en Excel.")

        # crear_fichero_csv()
        
        # Creo la cola y lanzo el procesador (encargado de ejecutar los PDFs de uno en uno)
        self.cola = Queue()
        threading.Thread(target=self.procesador, daemon=True).start()

        # Lanzo el Observador de la carpeta
        from watchdog.observers import Observer
        self.observer = Observer()
        self.event_handler = ProcesadorPDF(self.cola) # Este se encarga de las acciones cada vez que se detectan un nuevo PDF
        self.observer.schedule(self.event_handler, carpeta_monitoreo, recursive=False)
        self.observer.start()
        
        # self.setup_tray()

    # ESTO PARA CREAR EL PEQUEÑO ICONO EN LA ESQUINA
    # def setup_tray(self):
    #     img = Image.new('RGB', (64, 64), (255, 255, 255))
    #     d = ImageDraw.Draw(img)
    #     d.rectangle((10, 10, 54, 54), fill="green") # Icono verde para diferenciar
        
    #     self.tray_icon = Icon("PDFWatcher", img, menu=Menu(
    #         MenuItem('Mostrar', lambda: self.root.deiconify()),
    #         MenuItem('Salir', self.parar_monitor)
    #     ))
    #     threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    # Este procesador sirve para trabajar PDFs en orden de llegada a través de la cola
    def procesador(self):
    
        while True:
            ruta_pdf = self.cola.get() # Se bloquea aquí hasta que llegue un PDF
            procesar_nuevo_pdf(ruta_pdf, self.actualizar_ventana) # Procesa ese nuevo PDF
            self.cola.task_done() # Elimina ese PDF de la cola
    
    # Para actualizar el texto de la ventana
    def actualizar_ventana(self, text):
        # Usamos 'after' para que la actualización ocurra en el hilo principal
        self.root.after(0, lambda: self.status_var.set(text))
    
    # La función que finaliza el Monitor
    def parar_monitor(self):

        self.observer.stop() # Para el observador
        self.root.destroy() # Para el propio Monitor
        os._exit(0) # Salida forzosa para cerrar todos los hilos


if __name__ == "__main__":

    # Cargamos los datos de los alumnos (en este caso de un json)
    cargar_datos_json()

    # Si la carga de la base de datos de alumnos no funciona salta un mensaje de error y termina el programa
    if DICCIONARIO_JSON is None:
        root_temp = tk.Tk()
        root_temp.withdraw()
        messagebox.showerror("Error Crítico", "No se pudo cargar el archivo JSON o no existe.\nEl programa se detendrá.")
        sys.exit(1)
    
    # Lanzamiento del Monitor
    root = tk.Tk()
    app = AppMonitor(root)

    # Para que esté ejectuando siempre el Monitor
    root.mainloop()



