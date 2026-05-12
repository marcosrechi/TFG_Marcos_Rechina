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

# Variable para guardar la configuración elegida por el usuario
CONFIG = {}

# Variables globales usadas en el código
RUTA_FICHERO_DESTINO = None
DICCIONARIO_ALUMNOS = None

# Datos de correo origen
CORREO_ORIGEN = "pruebastfgmarcosrechina@gmail.com"
PASSWORD_ORIGEN = "jjao hbsb hvee jpqh"

# Nombre de la asignatura en cuestión (por defecto Informática)
NOMBRE_ASIGNATURA = "Informática"


# --------------------------------------------- TENGO QUE CAMBIARLO -----------------------------------------------------
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
                callback_status(f"Error en la obtención del número de matrícula del archivo {nombre_archivo}...")
                return None

            # Busca el número de matrícula en la base de datos y obtiene los datos del alumno
            callback_status(f"Comprobando informacion del alumno con matrícula {numero_matricula}...")
            datos_alumno = DICCIONARIO_ALUMNOS.get(numero_matricula)
            if datos_alumno is None:
                callback_status(f"Alumno con número de matrícula {numero_matricula} no enontrado")
            

            if CONFIG.get("enviar_correo") and datos_alumno:
                # Escribe el correo que funciona como justificante (solo si se encuentra al alumno correspondiente en la base de datos)
                callback_status(f"Mandando justificante por correo ...")
                mandar_correo(numero_matricula, datos_alumno)


            # Se actualiza el fichero con los datos del alumno detectado
            callback_status(f"Actualizando fichero ...")
            escribir_csv(numero_matricula, datos_alumno, ruta)

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
def escribir_csv(numero_matricula, datos_alumno, ruta_pdf):

    global RUTA_FICHERO_DESTINO

    # Para guardar la hora de entrega
    hora_entrega = time.strftime("%d/%m/%Y %H:%M", time.localtime())

    # Compruebo que datos se eligen guardar
    # Añadimos los nuevos según CONFIG si no estaban ya
    cabeceras_deseadas = ["Numero Matricula", "Nombre", "Correo"]
    if CONFIG.get("incluir_fecha_entrega"): cabeceras_deseadas.append("Hora Entrega")
    if CONFIG.get("incluir_nota"): cabeceras_deseadas.append("Nota")
    if CONFIG.get("incluir_ruta"): cabeceras_deseadas.append("Ruta Examen")

    base_de_datos_completa = []
    # Para asegurarnos de que exista la lista de cabeceras
    cabeceras_finales = list(cabeceras_deseadas)   
    
    # Si el fichero aún no existe, nos saltamos la parte de leer el existente y vamos directamente a escribir la nueva fila para crear el fichero por primera vez 
    if os.path.exists(RUTA_FICHERO_DESTINO):

        # Leo el fichero y guardo todos los datos
        try:
            # Abrimos el fichero y vemos si estánlas cabeceras deseadas
            with open(RUTA_FICHERO_DESTINO, mode='r', encoding='utf-8-sig') as f:

                # Guardo todos los datos de la base de datos
                lector = csv.DictReader(f, delimiter=';')

                # Guardo uno a uno los datos de cada fila en la variable
                for fila in lector:
                    base_de_datos_completa.append(fila)

                # Leo los encabezados del fichero
                if lector.fieldnames:

                    # Leo las cabeceras existentes 
                    cabeceras_existentes = lector.fieldnames

                    # Guardo las cabeceras en la lista final
                    for c in cabeceras_existentes:
                        if c not in cabeceras_finales:
                            cabeceras_finales.append(c)

                    # Y nos aseguramos de que las "deseadas" estén en la lista final (por si el CSV era viejo)
                    for c in cabeceras_deseadas:
                        if c not in cabeceras_finales:
                            cabeceras_finales.append(c)

        except Exception as e:
            print(f"Error leyendo archivo existente: {e}")
    
    # Busco en alumno en cuestión en el fichero de destino y actualizo la información en la variable
    alumno_encontrado = False
    for fila in base_de_datos_completa:
        if fila.get("Numero Matricula") == numero_matricula:

            # # Para actualizar el nombre y correo de la persona (NO ESTRICTAMENTE NECESARIO, NO DEBERÍA CAMBIAR)
            # if datos_alumno:
            #     fila["Nombre"] = datos_alumno.get("Nombre")
            #     fila["Correo"] = datos_alumno.get("Correo")

            # Actualizamos solo los campos elegidos por el usuario
            if CONFIG.get("incluir_fecha_entrega"): fila["Hora Entrega"] = hora_entrega
            if CONFIG.get("incluir_nota"): fila["Nota"] = "S/C"
            if CONFIG.get("incluir_ruta"): fila["Ruta Examen"] = ruta_pdf
            alumno_encontrado = True
            break
    
    # Si no se ha encontrado ningún alumno, añado una fila al final del listado
    if not alumno_encontrado:

       # Si se ha encontrado el alumno en la base de datos, entonces introducimos los datos en el fichero
        if datos_alumno:
            nueva_fila = {
                "Numero Matricula": numero_matricula,
                "Nombre": datos_alumno.get("Nombre"),
                "Correo": datos_alumno.get("Correo")
            }

        # Si no se ha encontrado el alumno en la base de datos previamente, entonces introducimos los datos en el fichero como "Alumno no encontrado"
        else:
            nueva_fila = {
                "Numero Matricula": numero_matricula,
                "Nombre": "Alumno no encontrado",
                "Correo": "Alumno no encontrado"
            }

        if CONFIG.get("incluir_fecha_entrega"): nueva_fila["Hora Entrega"] = hora_entrega
        if CONFIG.get("incluir_nota"): nueva_fila["Nota"] = "S/C"
        if CONFIG.get("incluir_ruta"): nueva_fila["Ruta Examen"] = ruta_pdf

        # Añadimos la nueva fila en la base de datos
        base_de_datos_completa.append(nueva_fila)

    # 4. Sobrescribir el archivo con TODO actualizado
    try:
        with open(RUTA_FICHERO_DESTINO, mode='w', newline='', encoding='utf-8-sig') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=cabeceras_finales, delimiter=';', extrasaction='ignore')
            escritor.writeheader() # Escribe las cabeceras (viejas + nuevas)
            escritor.writerows(base_de_datos_completa) # Escribe todas las filas
    except PermissionError:
        messagebox.showerror("Error", "El archivo está abierto en Excel. Ciérralo.")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado al guardar: {e}")

# Función encargadda de enviar el correo
def mandar_correo(numero_matricula, datos_alumno):

    # ----------- CAMBIAR LO DEL SERVER LEYENDO EL FINAL DEL CORREO -----------

    global CORREO_ORIGEN, PASSWORD_ORIGEN, NOMBRE_ASIGNATURA

    # Leo la parte final del correo (todo lo que esté detrás del @)
    correo_alumno = datos_alumno["Correo"].lower()
    tipo_correo = correo_alumno.split('@')[-1]
    
    # Buscamos si el dominio (lo que aparece detrás del @) contiene "hotmail" / "outlook" / "live"
    # Si no aparece, elegimos por defecto el servidor
    if any(p in tipo_correo for p in ["hotmail", "outlook", "live"]):
        smtp_server, smtp_port = "smtp.office365.com", 587          # Para correo basado en Outlook
    else:
        smtp_server, smtp_port = "smtp.gmail.com", 587              # Para correo basado en Gmail
    
    # Creamos el mensaje a enviar
    asunto = "Entrega de examen confirmada"
    cuerpo = f"Se confirma mediante el envío de este correo que el alumn@ {datos_alumno["Nombre"]} con matrícula {numero_matricula} ha realizado el examen de {NOMBRE_ASIGNATURA}"

    # Crear el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = CORREO_ORIGEN
    msg['To'] = correo_alumno
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        # Conexión al servidor
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Cifrado obligatorio para Office 365
        
        # Inicio de sesión
        server.login(CORREO_ORIGEN, PASSWORD_ORIGEN)
        
        # Envío del mensaje
        server.send_message(msg)
        print("¡Correo enviado con éxito!")
    
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Para asegurarse que se cierra el servidor del correo
    finally:
        server.quit()

    return

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
        self.root.title("Gestor de exámenes - Configuración Inicial")
        self.root.geometry("700x700")

        # Variables (Boolean variables a tiempo real) de las checkboxes
        self.checkbox_enviar_correo = tk.BooleanVar(value=True)
        self.checkbox_usar_correo_personalizado = tk.BooleanVar(value=False)
        self.checkbox_actualizar_fichero = tk.BooleanVar(value=True)
        self.checkbox_incluir_nota = tk.BooleanVar(value=False)
        self.checkbox_incluir_ruta = tk.BooleanVar(value=False)
        self.checkbox_incluir_fecha_entrega = tk.BooleanVar(value=False)
        self.checkbox_mostrar_password = tk.BooleanVar(value=False)
        self.texto_desplegable_formato_listado = tk.StringVar(value="CSV")
        
        # Variables (String variables a tiempo real) para guardar las rutas
        self.asignatura = tk.StringVar()
        self.ruta_monitoreo = tk.StringVar()
        self.ruta_listado = tk.StringVar()
        self.ruta_fichero_destino = tk.StringVar()
        self.email_usuario = tk.StringVar()
        self.password_usuario = tk.StringVar()
        

        self.dibujar_interfaz_opciones()

    # Función para dibujar la pantalla principal (selector de opciones)
    def dibujar_interfaz_opciones(self):
        # Limpiar frame
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Configuración de Funcionalidades", font=("Arial", 14, "bold")).pack(pady=10)

        # -------------------- SECCIÓN ASIGNATURA --------------------
        self.frame_asignatura = tk.LabelFrame(self.root, text="Datos Generales", padx=10, pady=10, fg="blue")
        self.frame_asignatura.pack(fill="x", padx=20, pady=5)
        tk.Label(self.frame_asignatura, text="Nombre de la Asignatura:").pack(side="left")
        tk.Entry(self.frame_asignatura, textvariable=self.asignatura, width=40).pack(side="left", padx=10)

        # -------------------- SECCIÓN CORREO --------------------
        self.frame_correo = tk.LabelFrame(self.root, text="Configuración de Correo", padx=10, pady=10)
        self.frame_correo.pack(fill="x", padx=20, pady=5)
        
        # Primera comprobacion: ¿Se envía el correo?
        # Cada vez que se clica se llama la función
        tk.Checkbutton(self.frame_correo, text="Enviar correo de confirmación", variable=self.checkbox_enviar_correo, command=self.habilitar_credenciales_correo).pack(anchor="w")

        # Frame para el "Correo Personalizado"
        self.frame_correo_personalizado = tk.Frame(self.frame_correo)
        tk.Checkbutton(self.frame_correo_personalizado, text="Usar su propio personalizado", variable=self.checkbox_usar_correo_personalizado, command=self.habilitar_credenciales_correo).pack(anchor="w", padx=20)
        
        # Frame para la entrada de correo y clave
        self.frame_credenciales = tk.Frame(self.frame_correo_personalizado)
        
        # Entrada de texto para la dirección de correo
        tk.Label(self.frame_credenciales, text="Email:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.frame_credenciales, textvariable=self.email_usuario, width=30).grid(row=0, column=1, padx=5, pady=2)

        # Entrada de texto para la contraseña de aplicación (lo guardo en una variable para poder mostrarla o no)
        tk.Label(self.frame_credenciales, text="Contraseña de aplicación:").grid(row=1, column=0, sticky="e")
        self.entrada_password = tk.Entry(self.frame_credenciales, textvariable=self.password_usuario, width=30, show="*")
        self.entrada_password.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Checkbutton(self.frame_credenciales, text="👁", variable=self.checkbox_mostrar_password, command=self.habilitar_ver_password).grid(row=1, column=2)
        
        self.habilitar_credenciales_correo()

        # -------------------- SECCIÓN CARPETA A MONITOREAR --------------------

        # Creando el frame para las rutas
        self.frame_monitoreo = tk.LabelFrame(self.root, text="Monitoreo de Archivos", padx=10, pady=10)
        self.frame_monitoreo.pack(fill="x", padx=20, pady=5)

        # Carpeta Monitoreo
        tk.Label(self.frame_monitoreo, text="Carpeta a Vigilar:").grid(row=2, column=0, sticky="w")
        tk.Entry(self.frame_monitoreo, textvariable=self.ruta_monitoreo, width=30).grid(row=2, column=1)
        tk.Button(self.frame_monitoreo, text="Examinar...", command=self.seleccionar_monitoreo).grid(row=2, column=2)


        # -------------------- SECCIÓN CONFIGURACIÓN FICHERO --------------------

        self.frame_config_fichero = tk.LabelFrame(self.root, text="Configuración del Listado de Alumnos/Fichero", padx=10, pady=10)
        self.frame_config_fichero.pack(fill="x", padx=20, pady=5)


        # Elegir tipo de listado de alumnos
        frame_tipo_listado = tk.Frame(self.frame_config_fichero)
        frame_tipo_listado.pack(fill="x")

        tk.Label(frame_tipo_listado, text="Formato:").pack(side="left")
        self.desplegable_formato_listado = ttk.Combobox(frame_tipo_listado, textvariable=self.texto_desplegable_formato_listado, values=["CSV", "JSON"], state="readonly", width=10)
        self.desplegable_formato_listado.pack(side="left", padx=10)

        # También elijo si se actualiza el listado ya existente
        self.checkbutton_actualizar_fichero = tk.Checkbutton(frame_tipo_listado, text="Actualizar información en el listado existente", variable=self.checkbox_actualizar_fichero, command=self.habilitar_csv_destino)
        self.checkbutton_actualizar_fichero.pack(side="left", padx=20)

        self.desplegable_formato_listado.bind("<<ComboboxSelected>>", self.comprobar_formato_listado) # Este .bind sirve para llamar a la función cada vez que se cambia la opción


        # Elegir ruta del Listado de Alumnos
        frame_ruta_listado = tk.Frame(self.frame_config_fichero)
        frame_ruta_listado.pack(fill="x")

        tk.Label(frame_ruta_listado, text="Listado de alumnos:").grid(row=1, column=0, sticky="w")
        tk.Entry(frame_ruta_listado, textvariable=self.ruta_listado, width=30).grid(row=1, column=1)
        tk.Button(frame_ruta_listado, text="Examinar...", command=self.seleccionar_listado).grid(row=1, column=2)


        # Elegir ruta del Fichero de Destino
        frame_ruta_destino = tk.Frame(self.frame_config_fichero)
        frame_ruta_destino.pack(fill="x")

        self.label_ruta_destino = tk.Label(frame_ruta_destino, text="Guardar Registro en:")
        self.label_ruta_destino.grid(row=3, column=0, sticky="w")
        self.entrada_ruta_destino = tk.Entry(frame_ruta_destino, textvariable=self.ruta_fichero_destino, width=30)
        self.entrada_ruta_destino.grid(row=3, column=1)
        self.boton_ruta_destino = tk.Button(frame_ruta_destino, text="Examinar...", command=self.seleccionar_csv_destino)
        self.boton_ruta_destino.grid(row=3, column=2)


        # ---------- SECCIÓN DATOS DEL FICHERO ----------
        frame_datos_fichero = tk.LabelFrame(self.root, text="Datos a añadir en el fichero", padx=10, pady=10)
        frame_datos_fichero.pack(fill="x", padx=20, pady=5)
        
        tk.Checkbutton(frame_datos_fichero, text="Incluir columna de Nota", variable=self.checkbox_incluir_nota).pack(anchor="w")
        tk.Checkbutton(frame_datos_fichero, text="Incluir columna de Ruta del examen", variable=self.checkbox_incluir_ruta).pack(anchor="w")
        tk.Checkbutton(frame_datos_fichero, text="Incluir columna de Fecha de entrega", variable=self.checkbox_incluir_fecha_entrega).pack(anchor="w")
        

        # ---------- BOTÓN PARA INICIAR EL MONITOREO ----------
        tk.Button(self.root, text="INICIAR MONITOREO", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.validar_e_iniciar).pack(pady=20)

        self.comprobar_formato_listado()

    # Función encargada de mostrar o no la entrada de texto para el correo
    def habilitar_credenciales_correo(self):
        
        # Primero comprobar si esta activada la opción de enviar correo
        if self.checkbox_enviar_correo.get():

            # Mostramos la opción de "Correo Personalizado"
            self.frame_correo_personalizado.pack(fill="x", pady=5)
            
            # Segundo comprobar si se utiliza un correo personalizado o no
            if self.checkbox_usar_correo_personalizado.get():

                # Si se quiere usar un correo personalizado, mostramos las entradas de texto
                self.frame_credenciales.pack(fill="x", pady=5, padx=40)
            else:

                # Si no se quiere usar un correo personalizado, no mostramos las entradas de texto
                self.frame_credenciales.pack_forget()

        else:
            # Si no se quiere enviar correo, escondemos TODO el bloque inferior
            self.frame_correo_personalizado.pack_forget()

            # También reseteamos la opción de usar correo personalizado
            self.checkbox_usar_correo_personalizado.set(False)

    # Función encargada de mostrar o no la contraseña
    def habilitar_ver_password(self):

        # Comprobamos si se quiere mostrar la contraseña
        if self.checkbox_mostrar_password.get():

            # Mostramos la contraseña tal como se escribe
            self.entrada_password.config(show="")

        else:

            # Mostrar solo asteriscos
            self.entrada_password.config(show="*")
    
    # Para comprobar el tipo de archivo y ocultar el checkbox acorde
    def comprobar_formato_listado(self, event=None):
        
        # Si el tipo de listado es JSON
        if self.texto_desplegable_formato_listado.get() == "JSON":

            # Ponemos la variable de actualizar fichero en false 
            self.checkbox_actualizar_fichero.set(False)

            # Desactivamos el checkbox
            self.checkbutton_actualizar_fichero.config(state="disabled")

        # Si el tipo de listado es CSV
        else:

            # Activamos el checkbox
            self.checkbutton_actualizar_fichero.config(state="normal")
        
        # Siempre actualizamos si se enseña o no la entrada de ruta de destino cuando cambiemos el tipo del listado
        self.habilitar_csv_destino() 

    # Función encargada de seleccionar el listado de alumnos
    def seleccionar_listado(self):

        # Coge el tipo de listado elegido y lo fuerza para elegir un tipo de archivo
        ext = "*.json" if self.texto_desplegable_formato_listado.get() == "JSON" else "*.csv"

        # Cuando se haya elegido una ruta se guarda en la variable
        ruta = filedialog.askopenfilename(title="Selecciona Listado de Alumnos", filetypes=[("Archivos de datos", ext)])
        if ruta: self.ruta_listado.set(ruta)

    # Función encargada de seleccionar la carpeta a monitorear
    def seleccionar_monitoreo(self):

        # Cuando se haya elegido una ruta se guarda en la variable
        ruta = filedialog.askdirectory()
        if ruta: self.ruta_monitoreo.set(ruta)

    # Función encargada de mostrar la selección de ruta de destino (siempre que se haya elegido NO actualizar el original)
    def habilitar_csv_destino(self):

        # Si el archivo es de tipo CSV y se ha elegido actualizar el fichero
        if self.texto_desplegable_formato_listado.get() == "CSV" and self.checkbox_actualizar_fichero.get():

            # No se muestran la entrada de ruta de destino de csv
            estado = "disabled"

            # Con esto limpiamos también la ruta que se haya elegido como destino (ya que no se usará)
            self.ruta_fichero_destino.set("")
        
        else:

            # Se muestran la entrada de ruta de destino de csv
            estado = "normal"

        # Se actualiza la config con la variable estado
        self.label_ruta_destino.config(state=estado)
        self.entrada_ruta_destino.config(state=estado)
        self.boton_ruta_destino.config(state=estado)

    # Función encargada de seleccionar la ruta donde se gaurdará el archivo (siempre que se haya elegido NO actualizar el original)
    def seleccionar_csv_destino(self):

        # Cuando se haya elegido una ruta se guarda en la variable
        ruta = filedialog.asksaveasfilename(title = "¿Dónde quieres guardar el fichero?", defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile = "Fichero_Alumnos.csv")
        if ruta: self.ruta_fichero_destino.set(ruta)

    # Comprobar si las rutas elegidas existen
    def validar_e_iniciar(self):

        # Si no ha escrito ninguna asignatura
        if not self.asignatura.get().strip():
            messagebox.showwarning("Datos incorrectos", "No se ha introducido ninguna asignatura")
            return

        # Si no existe la ruta de la carpeta
        if not os.path.isdir(self.ruta_monitoreo.get()):
            messagebox.showwarning("Datos incorrectos", "La carpeta a vigilar no existe o no es un directorio válido.")
            return

        # Si no existe el listado de alumnos
        if not os.path.isfile(self.ruta_listado.get()):
            messagebox.showwarning("Datos incorrectos", "El listado de alumnos no existe en la ruta especificada.")
            return

        if not self.checkbox_actualizar_fichero.get() and not os.path.isdir(os.path.dirname(self.ruta_fichero_destino.get())):
            messagebox.showwarning("Destino incorrecto", "La carpeta de destino para el fichero de registro no es válida.")
            return

        # MARCA_CAMBIO: LLAMADA A CARGAR_DATOS() PARA PROCESAR EL ARCHIVO ELEGIDO
        if not self.cargar_datos_listado():
            messagebox.showwarning("Error en la carga de datos", "Hubo un error en la carga de datos del listado de alumnos. Por favor, elija otro archivo")
            return


        global RUTA_FICHERO_DESTINO, CONFIG, CORREO_ORIGEN, PASSWORD_ORIGEN, NOMBRE_ASIGNATURA

        # Guardamos el nombre de la asignatura elegida
        NOMBRE_ASIGNATURA = self.asignatura.get().strip()

        # Guardamos las variables elegidas en las checkboxes
        CONFIG = {
            "enviar_correo": self.checkbox_enviar_correo.get(),
            "actualizar_fichero": self.checkbox_actualizar_fichero.get(),
            "incluir_nota": self.checkbox_incluir_nota.get(),
            "incluir_ruta": self.checkbox_incluir_ruta.get(),
            "incluir_fecha_entrega": self.checkbox_incluir_fecha_entrega.get()
        }

        # Si el usuario elige usar su correo personalizado, lo guardamos en la variable global
        if self.checkbox_usar_correo_personalizado.get():
            CORREO_ORIGEN = self.email_usuario.get()
            PASSWORD_ORIGEN = self.password_usuario.get()
        
        # Si el usuario elige actualizar el fichero, la ruta destino es la misma que origen
        if self.texto_desplegable_formato_listado.get() == "CSV" and self.checkbox_actualizar_fichero.get():
            RUTA_FICHERO_DESTINO = self.ruta_listado.get()
        
        # Si el usuario elige no actualizar el fichero, la ruta de destino es la elegida por el usuario
        else:
            RUTA_FICHERO_DESTINO = self.ruta_fichero_destino.get()

        # Una vez validados, limpiamos la ventana y creamos la nueva
        self.preparar_interfaz_monitoreo()

        # Después lanzamos la función encargada de verdad del monitoreo de la carpeta
        self.iniciar_logica_tras_configuracion()

    # Función encargada de cargar los datos del listado en la variable global
    def cargar_datos_listado(self):

        global DICCIONARIO_ALUMNOS
        ruta_listado = self.ruta_listado.get()
        formato_listado = self.texto_desplegable_formato_listado.get()

        # Dependiendo del tipo de formato que sea el listado
        try:
            # Si es de formato JSON
            if formato_listado == "JSON":
                with open(ruta_listado, "r", encoding="utf-8-sig") as f:
                    DICCIONARIO_ALUMNOS = json.load(f)
            
            # Si es de formato CSV
            else:
                # Si es CSV, lo convertimos a un diccionario para búsqueda rápida por matrícula
                DICCIONARIO_ALUMNOS = {}
                with open(ruta_listado, "r", encoding="utf-8-sig") as f:
                    
                    # Convierte el excel en un diccionario, usando la primera fila como los nombres de las llaves
                    lector = csv.DictReader(f, delimiter=';')

                    # Recorre las filas y las 
                    for fila in lector:
                        # Buscamos la columna que contenga "Matricula" o similar
                        id_alumno = fila.get("Numero Matricula") or fila.get("Matricula")
                        if id_alumno:
                            DICCIONARIO_ALUMNOS[id_alumno] = fila

            return True
        
        except Exception as e:
            messagebox.showerror("Error de lectura", f"No se pudo leer el archivo de alumnos:\n{e}")
            return False

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

        # Creo un icono en la bandeja de Windows
        # self.setup_tray()

    # Aquí arrancamos el Watchdog y la Cola con las rutas elegidas
    def iniciar_logica_tras_configuracion(self):

        # No para el monitoreo si cierras la ventana, se queda en segundo plano
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.withdraw()) # El "lambda" es para que se ejecute una vez que se cierre, no directamente

        # Creo la cola y lanzo el procesador (encargado de ejecutar los PDFs de uno en uno)
        self.cola = Queue()
        threading.Thread(target=self.procesador, daemon=True).start()

        # Lanzo el Observador de la carpeta
        self.observer = Observer()
        self.event_handler = ProcesadorPDF(self.cola) # Este se encarga de las acciones cada vez que se detectan un nuevo PDF
        self.observer.schedule(self.event_handler, self.ruta_monitoreo.get(), recursive=False)
        self.observer.start()
        
        # Creo un icono en la bandeja de Windows
        self.setup_tray()

    # Esto es para crear un pequeño iccono en la bandeja
    def setup_tray(self):
        # !!! CREAR UN ICONO SIMPLE (CUADRADO VERDE) !!!
        img = Image.new('RGB', (64, 64), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.rectangle((10, 10, 54, 54), fill="green")
        
        # !!! DEFINIR EL MENÚ DEL ICONO !!!
        menu = Menu(
            MenuItem("Mostrar Interfaz", lambda: self.root.after(0, self.root.deiconify)),  # El "lambda" es para que se ejecute una vez que se cierre, no directamente
            MenuItem("Detener y Salir", self.parar_monitor)
        )
        
        self.tray_icon = Icon("GestorExamenes", img, "Gestor de Exámenes", menu)
        
        # !!! LANZAR EN UN HILO APARTE PARA NO BLOQUEAR TKINTER !!!
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

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

        # Pruebo a eliminar el icono de la bandeja (si es que existe)
        try:
            self.tray_icon.stop()
        except:
            pass

        self.observer.stop() # Para el observador
        self.root.destroy() # Para el propio Monitor
        os._exit(0) # Salida forzosa para cerrar todos los hilos


if __name__ == "__main__":

    # Cargamos los datos de los alumnos (en este caso de un json)
    # cargar_datos_json()

    # # Si la carga de la base de datos de alumnos no funciona salta un mensaje de error y termina el programa
    # if DICCIONARIO_ALUMNOS is None:
    #     root_temp = tk.Tk()
    #     root_temp.withdraw()
    #     messagebox.showerror("Error Crítico", "No se pudo cargar el archivo JSON o no existe.\nEl programa se detendrá.")
    #     sys.exit(1)
    
    # Lanzamiento del Monitor
    root = tk.Tk()
    app = AppMonitor(root)

    # Para que esté ejectuando siempre el Monitor
    root.mainloop()



