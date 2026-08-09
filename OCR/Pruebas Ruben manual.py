# pip install tensorflow requests numpy

# AQUI VAS A QUITAR EL MARCO TU A MANO ANTES DE PASARLO POR EL RECONOCIMIENTO



import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.datasets import mnist
import cv2
import numpy as np
import requests
import fitz

import pytesseract


class DimensionesROI:
    def __init__(self, x, y, ancho, alto):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

def Cargar_Paginas_PDF(RutaPDF, dpi = 600):
    
    doc = fitz.open(RutaPDF)
    page = doc[0]
    mat = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
    pix = page.get_pixmap(matrix=mat)
    img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

    if pix.n == 4:  # RGBA
        img_data = cv2.cvtColor(img_data, cv2.COLOR_RGBA2RGB)
    else:  # RGB
        img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
    
    doc.close()

    return img_data

def Extraer_ROI_Iamgen(Imagen, Coordenadas):

    Recorte = Imagen[Coordenadas.y : Coordenadas.y + Coordenadas.alto, Coordenadas.x : Coordenadas.x + Coordenadas.ancho]

    return Recorte


# Paso 1: Descargar el modelo desde GitHub
url = "https://github.com/R4F405/Reconocimiento-de-Digitos-MNIST/raw/main/modelo_mnist.keras"
model_filename = "modelo_mnist.keras"
# ruta_imagen = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas\roi_extraida8.png"
RutaPDF7Seg = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Numero_7_Segmentos\test 7seg Epson_19092025163133 pag1.pdf"
# RutaPDFNormal = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Numero_A_Mano\Epson_12112025210213 8_Censurado.pdf"

# RutaPDFNormal = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Numero_A_Mano\Epson_12112025210213 2_Censurado.pdf"
RutaPDFNormal = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Numero_A_Mano\Epson_12112025210213 8_Censurado.pdf"
# RutaPDFNormal = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Numero_A_Mano\Epson_12112025210213 38_Censurado.pdf"

RutaImagenDestino = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas"
# RutaImagenDestino = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas"



# numero_esperado = [5, 6, 1, 0, 0]           # Para 2
numero_esperado = [5, 6, 8, 5, 9]           # Para 8
# numero_esperado = [5, 7, 7, 1, 5]           # Para 38

custom_config = r'--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'

iteracion = 1



print("Descargando modelo...")
response = requests.get(url)
with open(model_filename, "wb") as f:
    f.write(response.content)
print("Modelo descargado exitosamente.")

# Paso 2: Cargar el modelo
modelo = load_model(model_filename)
print("Modelo cargado correctamente.")

# Paso 3: Cargar el dataset MNIST para obtener una imagen de prueba
(_, _), (x_test, y_test) = mnist.load_data()



# # Seleccionar una imagen aleatoria
# idx = np.random.randint(0, len(x_test))
# imagen = x_test[idx]
# label_real = y_test[idx]

# # Preprocesar la imagen (normalización y reshape)
# imagen_normalizada = imagen / 255.0
# imagen_entrada = imagen_normalizada.reshape(1, 28, 28, 1)

# nombre_archivo_guardado = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas\PRUEBASORIGINALES.png"
# cv2.imwrite(nombre_archivo_guardado, imagen)

# # Paso 4: Realizar la predicción
# prediccion = modelo.predict(imagen_entrada)
# numero_predicho = np.argmax(prediccion)

# print(f"Etiqueta real: {label_real}")
# print(f"Número predicho por el modelo: {numero_predicho}")




# Ejemplo con imagen real

print(f"Intentando cargar: {RutaPDFNormal}")
Imagen = Cargar_Paginas_PDF(RutaPDFNormal)

# print(len(Paginas))

# Coordenadas de las 5 cifras
# CoordenadasROI = DimensionesROI(x = 445, y = 100, ancho = 85, alto = 30) # x, y, ancho, alto

# Coordenadas cada cifra
# CoordenadasROI = [
#     DimensionesROI(x = 484, y = 49, ancho = 12, alto = 18), # x, y, ancho, alto
#     DimensionesROI(x = 495, y = 49, ancho = 12, alto = 18),
#     DimensionesROI(x = 507, y = 49, ancho = 11, alto = 18),
#     DimensionesROI(x = 518, y = 49, ancho = 12, alto = 18),
#     DimensionesROI(x = 529, y = 49, ancho = 12, alto = 18)
# ]

# Para 8
CoordenadasROI = [
    DimensionesROI(x = 485, y = 51, ancho = 10, alto = 15), # x, y, ancho, alto
    DimensionesROI(x = 496, y = 51, ancho = 10, alto = 15),
    DimensionesROI(x = 508, y = 51, ancho = 9, alto = 15),
    DimensionesROI(x = 519, y = 51, ancho = 10, alto = 15),
    DimensionesROI(x = 530, y = 51, ancho = 10, alto = 15)
]

# Para 38
# CoordenadasROI = [
#     DimensionesROI(x = 483, y = 51, ancho = 10, alto = 14), # x, y, ancho, alto
#     DimensionesROI(x = 494, y = 51, ancho = 10, alto = 14),
#     DimensionesROI(x = 506, y = 51, ancho = 9, alto = 14),
#     DimensionesROI(x = 517, y = 51, ancho = 10, alto = 14),
#     DimensionesROI(x = 528, y = 51, ancho = 10, alto = 14)
# ]




# 2. Cargar la imagen DIRECTAMENTE en escala de grises
# El '0' o cv2.IMREAD_GRAYSCALE le dice a OpenCV: "ignora el color, dame B/N"
# imagen_original = cv2.imread(ruta_imagen, 0)



def preprocesar_para_tesseract(imagen_roi):
    # 1. Escala de grises
    gris = cv2.cvtColor(imagen_roi, cv2.COLOR_BGR2GRAY)
    
    # 2. AUMENTAR TAMAÑO (Upscaling)
    # Tesseract ODIA las imágenes de 28x28, son demasiado pequeñas.
    # Necesitamos que la imagen sea más grande para que vea bien los bordes.
    scale = 3 
    gris = cv2.resize(gris, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 3. Binarizar (OTSU)
    # NOTA: Tesseract prefiere fondo BLANCO y letra NEGRA.
    # Si tu ROI original es fondo blanco, NO inviertas.
    # Si usas THRESH_BINARY (sin INV), obtienes fondo blanco y letra negra si la entrada era así.
    _, thresh = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 4. LIMPIEZA DE BORDES (Igual que antes, para quitar el marco)
    h, w = thresh.shape
    margen = 5 # Aumentamos margen porque hemos escalado la imagen x3
    thresh[0:margen, :] = 255       # Pintamos de BLANCO (fondo)
    thresh[h-margen:h, :] = 255
    thresh[:, 0:margen] = 255
    thresh[:, w-margen:w] = 255

    # 5. DILATACIÓN SUAVE (Opcional)
    # Si la letra quedó muy fina, la engordamos un poco (Erosionar en modo fondo blanco engorda la letra negra)
    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.erode(thresh, kernel, iterations=1)

    # 6. AÑADIR UN BORDE BLANCO ALREDEDOR (Padding)
    # A Tesseract no le gusta que la letra toque el borde de la imagen.
    thresh = cv2.copyMakeBorder(thresh, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)

    # NO normalizamos (/255) ni hacemos reshape. Devolvemos la imagen uint8 tal cual.
    return thresh




# --- PRIMER INTENTO DE NUEVA FUNCIÓN DE PREPROCESAMIENTO PARA MNIST ---

def preprocesar_para_mnist(imagen_roi):
    # 1. Convertir a escala de grises
    gris = cv2.cvtColor(imagen_roi, cv2.COLOR_BGR2GRAY)
    
    # 2. Reescalar un poco antes de procesar si es muy pequeña (opcional pero ayuda)
    # Factor de escala (si la ROI original es muy chica, ej: 12px)
    scale = 2 
    gris = cv2.resize(gris, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 3. Invertir colores (MNIST es blanco sobre negro)
    gris = cv2.bitwise_not(gris)
    
    # 4. Binarizar (Thresholding) para limpiar 'ruido' gris
    # Esto deja el número blanco puro y fondo negro puro
    _, thresh = cv2.threshold(gris, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    # 5. MANTENER RELACIÓN DE ASPECTO (Padding)
    # Queremos meter la imagen rectangular en un cuadrado negro sin estirarla
    filas, cols = thresh.shape
    
    if filas > cols:
        factor = 20.0 / filas
        filas_nuevas = 20
        cols_nuevas = int(cols * factor)
    else:
        factor = 20.0 / cols
        cols_nuevas = 20
        filas_nuevas = int(filas * factor)
        
    # Redimensionar a max 20x20 (dejando margen para llegar a 28x28)
    img_mini = cv2.resize(thresh, (cols_nuevas, filas_nuevas), interpolation=cv2.INTER_AREA)
    
    # Crear imagen negra de 28x28
    imagen_final = np.zeros((28, 28), dtype=np.uint8)
    
    # Calcular centro para pegar el número
    col_centro = (28 - cols_nuevas) // 2
    fila_centro = (28 - filas_nuevas) // 2
    
    # Pegar el número redimensionado en el centro del cuadro negro
    imagen_final[fila_centro:fila_centro+filas_nuevas, col_centro:col_centro+cols_nuevas] = img_mini
    
    # 6. Normalizar
    imagen_final = imagen_final / 255.0
    imagen_final = imagen_final.reshape(1, 28, 28, 1)
    
    return imagen_final, thresh # Devolvemos thresh solo para guardar la foto y verla



# --- TU BUCLE MODIFICADO ---

for i, (Coordenada, cifra_esperada) in enumerate(zip(CoordenadasROI, numero_esperado)):
    
    # NOTA: Si subiste el DPI a 300, multiplica tus coordenadas aquí
    # factor_correccion = 2 # Si pasaste de 150 a 300 dpi
    # Coordenada.x *= factor_correccion
    # Coordenada.y *= factor_correccion
    # ... etc

    Zona7segmentos = Extraer_ROI_Iamgen(Imagen, Coordenada)

    if Zona7segmentos is None:
        print("¡ERROR! ROI vacía.")
        continue

    nombre_archivo = rf"{RutaImagenDestino}\ZonaRaw_Cifra_{i+1}.png"
    cv2.imwrite(nombre_archivo, Zona7segmentos)

    # Usamos la nueva función de preprocesamiento
    imagen_entrada, imagen_debug = preprocesar_para_mnist(Zona7segmentos)
    # imagen_entrada = preprocesar_para_tesseract(Zona7segmentos)
    # imagen_entrada_inv = cv2.bitwise_not(imagen_entrada)
    
    # Tesseract    # texto = pytesseract.image_to_string(imagen_entrada, config=custom_config)
    # texto = pytesseract.image_to_string(imagen_entrada_inv, config=custom_config)
    # numero_predicho = texto.strip()

    # Modelo MNIST
    prediccion = modelo.predict(imagen_entrada, verbose=0) # verbose=0 quita el log de keras
    numero_predicho = np.argmax(prediccion)

    print(f"--- Cifra {i+1} ---")
    print(f"Real: {cifra_esperada} | Predicho: {numero_predicho}")
    # print(f"Confianza: {confianza:.2f}%")

    # Guardar imagen para depuración (La que realmente ve el modelo antes de normalizar)
    # nombre_archivo = rf"{RutaImagenDestino}\Cifra_{i+1}_Esperado_{cifra_esperada}_Obtenido_{numero_predicho}.png"
    # Guardamos la imagen cuadrada de 28x28 (des-normalizada para verla bien)
    # cv2.imwrite(nombre_archivo, (imagen_entrada.reshape(28,28) * 255).astype(np.uint8))
    nombre_archivo = rf"{RutaImagenDestino}\Cifra_{i+1}_Esperado_{cifra_esperada}_Obtenido_{numero_predicho}_Tesseract.png"
    # cv2.imwrite(nombre_archivo, imagen_entrada)
    # cv2.imwrite(nombre_archivo, imagen_entrada_inv)
    
    # Gaurdamos exactamente la imagen que devuelve la función de preprocesamiento para MNIST (imagen_final, exactamente la que se le pasa al modelo)
    cv2.imwrite(nombre_archivo, (imagen_entrada.reshape(28,28) * 255).astype(np.uint8))

    


    # cv2.imwrite(nombre_archivo, (imagen_entrada.reshape(28,28) * 255).astype(np.uint8))

    
    if str(cifra_esperada) != numero_predicho and cifra_esperada != numero_predicho:
        print("⚠️ FALLO DETECTADO")




