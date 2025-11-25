# pip install tensorflow requests numpy

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.datasets import mnist
import cv2
import numpy as np
import requests
import fitz


class DimensionesROI:
    def __init__(self, x, y, ancho, alto):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

def Cargar_Paginas_PDF(RutaPDF, dpi = 150):
    
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
RutaPDF7Seg = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\test 7seg Epson_19092025163133 pag1.pdf"
RutaPDFNormal = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Epson_12112025210213 8_Censurado.pdf"
RutaImagenDestino = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas"
numero_esperado = [5, 6, 8, 5, 9]

iteracion = 2



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
CoordenadasROI = [
    DimensionesROI(x = 485 + 12 * 0, y = 50, ancho = 12, alto = 15), # x, y, ancho, alto
    DimensionesROI(x = 485 + 12 * 1, y = 50, ancho = 12, alto = 15),
    DimensionesROI(x = 485 + 12 * 2, y = 50, ancho = 12, alto = 15),
    DimensionesROI(x = 485 + 12 * 3, y = 50, ancho = 12, alto = 15),
    DimensionesROI(x = 485 + 12 * 4, y = 50, ancho = 12, alto = 15)
]


Zona7segmentos = Extraer_ROI_Iamgen(Imagen, CoordenadasROI[iteracion])

# 2. Cargar la imagen DIRECTAMENTE en escala de grises
# El '0' o cv2.IMREAD_GRAYSCALE le dice a OpenCV: "ignora el color, dame B/N"
# imagen_original = cv2.imread(ruta_imagen, 0)

# Verificación de seguridad
if Zona7segmentos is None:
    print("¡ERROR! No se encontró la imagen. Revisa la ruta.")
    # Aquí deberías detener el programa en un caso real
else:
    print(f"Imagen cargada. Tamaño original: {Zona7segmentos.shape}")

    # 3. Redimensionar a 28x28 (Obligatorio)
    # Esto fuerza la imagen a 28x28 píxeles, sin importar cómo era antes.
    # 'interpolation=cv2.INTER_AREA' es bueno para reducir tamaños sin perder detalle.

    Zona7segmentos_gris = cv2.cvtColor(Zona7segmentos, cv2.COLOR_BGR2GRAY)

    imagen_28x28 = cv2.resize(Zona7segmentos_gris, (28, 28), interpolation=cv2.INTER_AREA)
    print(f"Imagen redimensionada")

    # --- PASO CRÍTICO: INVERSIÓN DE COLORES ---
    # El dataset MNIST (con el que se entrenó el modelo) son números BLANCOS sobre fondo NEGRO.
    # Un escaneo de papel es un número NEGRO sobre fondo BLANCO.
    # ¡Tenemos que invertir los colores o el modelo fallará!
    imagen_invertida = cv2.bitwise_not(imagen_28x28)
    print(f"Inversión de colores completado")

    nombre_archivo_guardado = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas\NUMEROALEER.png"
    
    print(f"Imagen guardada como: {nombre_archivo_guardado}")

    # Preprocesar la imagen (normalización y reshape)
    imagen_normalizada = imagen_invertida / 255.0
    imagen_entrada = imagen_normalizada.reshape(1, 28, 28, 1)

    cv2.imwrite(nombre_archivo_guardado, imagen_invertida)

    # Paso 4: Realizar la predicción
    prediccion = modelo.predict(imagen_entrada)
    numero_predicho = np.argmax(prediccion)


print(f"Etiqueta real: {numero_esperado[iteracion]}")
print(f"Número predicho por el modelo: {numero_predicho}")

