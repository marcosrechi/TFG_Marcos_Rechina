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
RutaPDFNormal = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Epson_12112025210213 38_Censurado.pdf"
RutaImagenDestino = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas"
# numero_esperado = [5, 6, 8, 5, 9]
numero_esperado = [5, 7, 7, 1, 5]

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

# Coordenadas de ejemplo 38
# CoordenadasROI = [
#     DimensionesROI(x = 484, y = 49, ancho = 12, alto = 18), # x, y, ancho, alto
#     DimensionesROI(x = 495, y = 49, ancho = 12, alto = 18),
#     DimensionesROI(x = 507, y = 49, ancho = 11, alto = 18),
#     DimensionesROI(x = 518, y = 49, ancho = 12, alto = 18),
#     DimensionesROI(x = 529, y = 49, ancho = 12, alto = 18)
# ]


# Coordenadas de ejemplo 38
CoordenadasROI = [
    DimensionesROI(x = 482, y = 49, ancho = 12, alto = 18), # x, y, ancho, alto
    DimensionesROI(x = 493, y = 49, ancho = 12, alto = 18),
    DimensionesROI(x = 505, y = 49, ancho = 11, alto = 18),
    DimensionesROI(x = 516, y = 49, ancho = 12, alto = 18),
    DimensionesROI(x = 527, y = 49, ancho = 12, alto = 18)
]




# 2. Cargar la imagen DIRECTAMENTE en escala de grises
# El '0' o cv2.IMREAD_GRAYSCALE le dice a OpenCV: "ignora el color, dame B/N"
# imagen_original = cv2.imread(ruta_imagen, 0)





# --- NUEVA VERSIÓN MEJORADA DE LA FUNCIÓN DE PREPROCESAMIENTO PARA MNIST ---

# ---------------------------------------------------------------------------------------------



# # --- FUNCIÓN DE PREPROCESAMIENTO "QUIRÚRGICO" ---
# def procesar_para_mnist_final(imagen_roi):
#     # 1. Escala de grises
#     gris = cv2.cvtColor(imagen_roi, cv2.COLOR_BGR2GRAY)
    
#     # 2. Invertir y Binarizar (OTSU) -> Fondo Negro, Letra Blanca
#     # Bitwise_not porque el PDF es tinta negra sobre blanco
#     _, thresh = cv2.threshold(cv2.bitwise_not(gris), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

#     # 3. ELIMINAR EL MARCO (Busca contornos)
#     contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     if not contornos:
#         return None, thresh # Devuelve lo que tenga si falla la detección

#     # Buscamos el contorno más grande
#     c_mejor = max(contornos, key=cv2.contourArea)
#     x, y, w, h = cv2.boundingRect(c_mejor)
    
#     h_img, w_img = thresh.shape
    
#     # Lógica anti-marco: Si el contorno ocupa casi toda la imagen (>85%), es el borde.
#     # En ese caso, recortamos unos píxeles y buscamos de nuevo dentro.
#     if w > w_img * 0.85 or h > h_img * 0.85:
#         margen = 3
#         thresh_recortado = thresh[margen:h_img-margen, margen:w_img-margen]
#         contornos_inner, _ = cv2.findContours(thresh_recortado, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
#         if contornos_inner:
#             c_mejor = max(contornos_inner, key=cv2.contourArea)
#             x, y, w, h = cv2.boundingRect(c_mejor)
#             # Ajustamos coordenadas relativas al recorte
#             x += margen
#             y += margen
#             roi_numero = thresh[y:y+h, x:x+w]
#         else:
#             roi_numero = thresh # Fallback: usamos la imagen entera
#     else:
#         # El contorno ya era el número limpio
#         roi_numero = thresh[y:y+h, x:x+w]

#     # 4. REDIMENSIONAR MANTENIENDO PROPORCIÓN (Aspect Ratio)
#     # El número debe caber en 20x20 pixeles para no tocar bordes en la imagen de 28x28
#     h_roi, w_roi = roi_numero.shape
#     if h_roi == 0 or w_roi == 0: return None, thresh

#     factor = 20.0 / max(h_roi, w_roi)
#     nuevo_h, nuevo_w = int(h_roi * factor), int(w_roi * factor)
    
#     roi_resized = cv2.resize(roi_numero, (nuevo_w, nuevo_h), interpolation=cv2.INTER_AREA)

#     # 5. CREAR IMAGEN FINAL 28x28 FONDO NEGRO Y CENTRAR
#     imagen_final = np.zeros((28, 28), dtype=np.uint8)
    
#     col_centro = (28 - nuevo_w) // 2
#     fila_centro = (28 - nuevo_h) // 2
#     imagen_final[fila_centro:fila_centro+nuevo_h, col_centro:col_centro+nuevo_w] = roi_resized

#     # 6. Normalizar para el modelo
#     imagen_input = imagen_final / 255.0
#     imagen_input = imagen_input.reshape(1, 28, 28, 1)

#     return imagen_input, imagen_final



# ---------------------------------------------------------------------------------------------





def procesar_para_mnist_final(imagen_roi):
    # 1. Escala de grises
    gris = cv2.cvtColor(imagen_roi, cv2.COLOR_BGR2GRAY)
    
    # 2. Invertir y Binarizar (Fondo negro, Numero blanco)
    # Usamos OTSU para que el umbral sea automático según la luz
    _, thresh = cv2.threshold(cv2.bitwise_not(gris), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    h_img, w_img = thresh.shape

    # 3. LIMPIEZA DE BORDES (MASKING) - SIN MORFOLOGÍA
    # Simplemente ponemos a negro (0) un marco de seguridad de 2 píxeles.
    # Esto elimina el recuadro del PDF sin deformar el número interior.
    margen = 2 
    thresh[0:margen, :] = 0             # Arriba
    thresh[h_img-margen:h_img, :] = 0   # Abajo
    thresh[:, 0:margen] = 0             # Izquierda
    thresh[:, w_img-margen:w_img] = 0   # Derecha

    # 4. ENCONTRAR EL NÚMERO (Bounding Box de todo lo blanco)
    # En lugar de contornos complejos, buscamos TODOS los puntos que no sean negros.
    puntos = cv2.findNonZero(thresh)
    
    if puntos is None:
        return None, thresh # Si la imagen quedó negra entera

    # Obtenemos el rectángulo que encierra a TODOS los puntos blancos restantes
    x, y, w, h = cv2.boundingRect(puntos)
    
    # Filtro anti-ruido mínimo: Si lo que queda es una mota de polvo (<3 pixeles), fuera
    if w < 3 or h < 5:
        return None, thresh

    # Recortamos el número limpio
    roi_numero = thresh[y:y+h, x:x+w]

    # 5. REDIMENSIONAR (MANTENIENDO PROPORCIÓN)
    # Esto es CRUCIAL para MNIST. No estiramos.
    h_roi, w_roi = roi_numero.shape
    
    # Factor para que la dimensión más grande sea 20px (dejando margen en la caja de 28)
    factor = 20.0 / max(h_roi, w_roi)
    nuevo_h, nuevo_w = int(h_roi * factor), int(w_roi * factor)
    
    # Evitar errores de redondeo a 0
    if nuevo_h <= 0: nuevo_h = 1
    if nuevo_w <= 0: nuevo_w = 1

    roi_resized = cv2.resize(roi_numero, (nuevo_w, nuevo_h), interpolation=cv2.INTER_AREA)

    # 6. PEGAR EN EL CENTRO DE UNA CAJA NEGRA 28x28
    imagen_final = np.zeros((28, 28), dtype=np.uint8)
    
    col_centro = (28 - nuevo_w) // 2
    fila_centro = (28 - nuevo_h) // 2
    
    imagen_final[fila_centro:fila_centro+nuevo_h, col_centro:col_centro+nuevo_w] = roi_resized

    # 7. Normalizar
    imagen_input = imagen_final / 255.0
    imagen_input = imagen_input.reshape(1, 28, 28, 1)

    return imagen_input, imagen_final







# ---------------------------------------------------------------------------------------------

# NO ESTA NADA MAL ESTA OPCION

# def procesar_para_mnist_final(imagen_roi):
#     # 1. Escala de grises
#     gris = cv2.cvtColor(imagen_roi, cv2.COLOR_BGR2GRAY)
    
#     # 2. Invertir y Binarizar (OTSU) -> Fondo Negro, Letra Blanca
#     _, thresh = cv2.threshold(cv2.bitwise_not(gris), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
#     h_img, w_img = thresh.shape

#     # --- PASO NUEVO: AFEITADO DE BORDES (MASKING) ---
#     # Pintamos de negro un margen de seguridad alrededor.
#     # Esto elimina los restos del marco y SEPARA el número del borde si lo está tocando.
#     # Dado que tu ROI es pequeña (aprox 12x18), borramos 2 o 3 pixeles.
#     margen_seguridad = 2 
    
#     # Crear una máscara negra para borrar los bordes
#     thresh[0:margen_seguridad, :] = 0  # Borde superior
#     thresh[h_img-margen_seguridad:h_img, :] = 0 # Borde inferior
#     thresh[:, 0:margen_seguridad] = 0  # Borde izquierdo
#     thresh[:, w_img-margen_seguridad:w_img] = 0 # Borde derecho

#     # 3. MORFOLOGÍA (SANADO)
#     # Al borrar los bordes, quizás cortamos la punta de un 5 o un 7.
#     # Usamos 'Dilate' suave para recuperar volumen o 'Close' para cerrar huecos.
#     kernel = np.ones((2,2), np.uint8)
#     thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

#     # 4. DETECTAR CONTORNOS
#     contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     if not contornos:
#         return None, thresh 

#     # --- LÓGICA DE CENTROIDE ---
#     # En lugar de buscar el más grande, buscamos el que esté más cerca del CENTRO de la imagen.
#     centro_img_x = w_img // 2
#     centro_img_y = h_img // 2
    
#     mejor_contorno = None
#     menor_distancia = float('inf')
    
#     for c in contornos:
#         x, y, w, h = cv2.boundingRect(c)
#         area = w * h
        
#         # Descartar ruido muy pequeño (puntos sucios)
#         if area < 5: continue
            
#         # Calcular el centro de este contorno
#         cx = x + w // 2
#         cy = y + h // 2
        
#         # Calcular distancia al centro de la imagen (Teorema Pitágoras)
#         distancia = math.sqrt((cx - centro_img_x)**2 + (cy - centro_img_y)**2)
        
#         # Priorizamos el objeto central. 
#         # (Opcional: puedes ponderar también el área si quieres)
#         if distancia < menor_distancia:
#             menor_distancia = distancia
#             mejor_contorno = c

#     if mejor_contorno is None:
#         return None, thresh

#     # Recortar el ganador
#     x, y, w, h = cv2.boundingRect(mejor_contorno)
#     roi_numero = thresh[y:y+h, x:x+w]

#     # 5. REDIMENSIONAR MANTENIENDO PROPORCIÓN (Igual que antes)
#     h_roi, w_roi = roi_numero.shape
#     if h_roi == 0 or w_roi == 0: return None, thresh

#     factor = 20.0 / max(h_roi, w_roi)
#     nuevo_h, nuevo_w = int(h_roi * factor), int(w_roi * factor)
    
#     roi_resized = cv2.resize(roi_numero, (nuevo_w, nuevo_h), interpolation=cv2.INTER_AREA)

#     # 6. CENTRAR EN 28x28
#     imagen_final = np.zeros((28, 28), dtype=np.uint8)
#     col_centro = (28 - nuevo_w) // 2
#     fila_centro = (28 - nuevo_h) // 2
    
#     # Pegado seguro
#     end_y = min(fila_centro+nuevo_h, 28)
#     end_x = min(col_centro+nuevo_w, 28)
#     imagen_final[fila_centro:end_y, col_centro:end_x] = roi_resized[0:end_y-fila_centro, 0:end_x-col_centro]

#     # 7. Normalizar
#     imagen_input = imagen_final / 255.0
#     imagen_input = imagen_input.reshape(1, 28, 28, 1)

#     return imagen_input, imagen_final

# ---------------------------------------------------------------------------------------------







# --- BUCLE PRINCIPAL ---

print(f"Procesando {len(CoordenadasROI)} cifras...")

for i, (Coordenada, cifra_esperada) in enumerate(zip(CoordenadasROI, numero_esperado)):

    # 1. Extraer recorte crudo del PDF
    ZonaRaw = Extraer_ROI_Iamgen(Imagen, Coordenada)

    nombre_archivo = rf"{RutaImagenDestino}\ZonaRaw_Cifra_{i+1}.png"
    cv2.imwrite(nombre_archivo, ZonaRaw)

    if ZonaRaw is None or ZonaRaw.size == 0:
        print(f"Error: ROI {i+1} vacía.")
        continue

    # 2. Preprocesar (Quitar marco y centrar)
    img_input, imagen_debug = procesar_para_mnist_final(ZonaRaw)
    
    if img_input is None:
        print(f"Cifra {i+1}: No se detectó dígito.")
        continue

    # 3. Predecir
    prediccion = modelo.predict(img_input, verbose=0)
    numero_predicho = np.argmax(prediccion)
    confianza = np.max(prediccion) * 100

    # 4. Guardar imagen con el nombre solicitado
    nombre_archivo = rf"{RutaImagenDestino}\Cifra_{i+1}_Esperado_{cifra_esperada}_Obtenido_{numero_predicho}.png"
    cv2.imwrite(nombre_archivo, imagen_debug)

    # Imprimir resultado en consola
    estado = "✅" if numero_predicho == cifra_esperada else "❌"
    print(f"Cifra {i+1} [{estado}] | Real: {cifra_esperada} -> Pred: {numero_predicho} ({confianza:.1f}%)")
    print(f"   -> Guardado: Cifra_{i+1}_Esperado_{cifra_esperada}_Obtenido_{numero_predicho}.png")

print("\n--- Proceso finalizado ---")













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

