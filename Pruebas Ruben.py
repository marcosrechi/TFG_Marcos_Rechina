# pip install tensorflow requests numpy

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.datasets import mnist
import cv2
import numpy as np
import requests
import fitz


import math


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
RutaPDF7Seg = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\test 7seg Epson_19092025163133 pag1.pdf"
# RutaPDFNormal = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Epson_12112025210213 8_Censurado.pdf"
RutaPDFNormal = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Epson_12112025210213 8_Censurado.pdf"
RutaImagenDestino = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas"
numero_esperado = [5, 6, 8, 5, 9]

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


CoordenadasROI = [
    DimensionesROI(x = 484, y = 49, ancho = 12, alto = 18), # x, y, ancho, alto
    DimensionesROI(x = 495, y = 49, ancho = 12, alto = 18),
    DimensionesROI(x = 507, y = 49, ancho = 11, alto = 18),
    DimensionesROI(x = 518, y = 49, ancho = 12, alto = 18),
    DimensionesROI(x = 529, y = 49, ancho = 12, alto = 18)
]




# 2. Cargar la imagen DIRECTAMENTE en escala de grises
# El '0' o cv2.IMREAD_GRAYSCALE le dice a OpenCV: "ignora el color, dame B/N"
# imagen_original = cv2.imread(ruta_imagen, 0)




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

    # Usamos la nueva función de preprocesamiento
    imagen_entrada, imagen_debug = preprocesar_para_mnist(Zona7segmentos)

    # Predicción
    prediccion = modelo.predict(imagen_entrada, verbose=0) # verbose=0 quita el log de keras
    numero_predicho = np.argmax(prediccion)
    confianza = np.max(prediccion) * 100

    print(f"--- Cifra {i+1} ---")
    print(f"Real: {cifra_esperada} | Predicho: {numero_predicho}")
    print(f"Confianza: {confianza:.2f}%")

    # Guardar imagen para depuración (La que realmente ve el modelo antes de normalizar)
    nombre_archivo = rf"{RutaImagenDestino}\Cifra_{i+1}_Esperado_{cifra_esperada}_Obtenido_{numero_predicho}.png"
    # Guardamos la imagen cuadrada de 28x28 (des-normalizada para verla bien)
    cv2.imwrite(nombre_archivo, (imagen_entrada.reshape(28,28) * 255).astype(np.uint8))


    
    if cifra_esperada != numero_predicho:
        print("⚠️ FALLO DETECTADO")











# for Coordenada, cifra_esperada in zip(CoordenadasROI, numero_esperado):

#     Zona7segmentos = Extraer_ROI_Iamgen(Imagen, Coordenada)

#     if Zona7segmentos is None:
#         print("¡ERROR! No se encontró la imagen. Revisa la ruta.")
#         # Aquí deberías detener el programa en un caso real
    
#     else:

#         print(f"Cifra numero {iteracion}")

#         Zona7segmentos_gris = cv2.cvtColor(Zona7segmentos, cv2.COLOR_BGR2GRAY)

#         imagen_28x28 = cv2.resize(Zona7segmentos_gris, (28, 28), interpolation=cv2.INTER_AREA)
#         # print(f"Imagen redimensionada")

#         # --- PASO CRÍTICO: INVERSIÓN DE COLORES ---
#         # El dataset MNIST (con el que se entrenó el modelo) son números BLANCOS sobre fondo NEGRO.
#         # Un escaneo de papel es un número NEGRO sobre fondo BLANCO.
#         # ¡Tenemos que invertir los colores o el modelo fallará!
#         imagen_invertida = cv2.bitwise_not(imagen_28x28)
#         # print(f"Inversión de colores completado")

#         # nombre_archivo_guardado = rf"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas\NUMERO_A_LEER_{iteracion}.png"
#         nombre_archivo_guardado = rf"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas\NUMERO_A_LEER_{iteracion}.png"
#         iteracion += 1

#         # print(f"Imagen guardada como: {nombre_archivo_guardado}")

#         # Preprocesar la imagen (normalización y reshape)
#         imagen_normalizada = imagen_invertida / 255.0
#         imagen_entrada = imagen_normalizada.reshape(1, 28, 28, 1)

#         cv2.imwrite(nombre_archivo_guardado, imagen_invertida)

#         # Paso 4: Realizar la predicción
#         prediccion = modelo.predict(imagen_entrada)
#         numero_predicho = np.argmax(prediccion)


#         print(f"Etiqueta real: {cifra_esperada}")
#         print(f"Número predicho por el modelo: {numero_predicho}\n")



# Zona7segmentos = Extraer_ROI_Iamgen(Imagen, CoordenadasROI[iteracion])

# # Verificación de seguridad
# if Zona7segmentos is None:
#     print("¡ERROR! No se encontró la imagen. Revisa la ruta.")
#     # Aquí deberías detener el programa en un caso real
# else:

#     for Coordenada, cifra in CoordenadasROI, numero_esperado:

#         Zona7segmentos = Extraer_ROI_Iamgen(Imagen, Coordenada)

#     # print(f"Imagen cargada. Tamaño original: {Zona7segmentos.shape}")

#     # 3. Redimensionar a 28x28 (Obligatorio)
#     # Esto fuerza la imagen a 28x28 píxeles, sin importar cómo era antes.
#     # 'interpolation=cv2.INTER_AREA' es bueno para reducir tamaños sin perder detalle.

#     Zona7segmentos_gris = cv2.cvtColor(Zona7segmentos, cv2.COLOR_BGR2GRAY)

#     imagen_28x28 = cv2.resize(Zona7segmentos_gris, (28, 28), interpolation=cv2.INTER_AREA)
#     print(f"Imagen redimensionada")

#     # --- PASO CRÍTICO: INVERSIÓN DE COLORES ---
#     # El dataset MNIST (con el que se entrenó el modelo) son números BLANCOS sobre fondo NEGRO.
#     # Un escaneo de papel es un número NEGRO sobre fondo BLANCO.
#     # ¡Tenemos que invertir los colores o el modelo fallará!
#     imagen_invertida = cv2.bitwise_not(imagen_28x28)
#     print(f"Inversión de colores completado")

#     nombre_archivo_guardado = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas\NUMEROALEER.png"
    
#     print(f"Imagen guardada como: {nombre_archivo_guardado}")

#     # Preprocesar la imagen (normalización y reshape)
#     imagen_normalizada = imagen_invertida / 255.0
#     imagen_entrada = imagen_normalizada.reshape(1, 28, 28, 1)

#     cv2.imwrite(nombre_archivo_guardado, imagen_invertida)

#     # Paso 4: Realizar la predicción
#     prediccion = modelo.predict(imagen_entrada)
#     numero_predicho = np.argmax(prediccion)


# print(f"Etiqueta real: {numero_esperado[iteracion]}")
# print(f"Número predicho por el modelo: {numero_predicho}")

