import fitz
import cv2
import numpy as np
import os


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

def leer_dni_omr_con_x(imagen):
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 1. Umbralización (igual que antes)
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    # --- NUEVO PASO: DILATACIÓN ---
    
    # Definimos un "kernel". Es la forma del "pincel" que usaremos para engordar.
    # Un kernel de (3,3) o (5,5) suele funcionar bien.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    
    # Aplicamos la dilatación.
    # iterations=2 significa que aplicamos el engorde dos veces para asegurar.
    thresh_dilatado = cv2.dilate(thresh, kernel, iterations=2)
    
    # ------------------------------
    
    # IMPORTANTE: Ahora pasas 'thresh_dilatado' a tu función de contar,
    # NO la 'thresh' original.
    return imagen, thresh_dilatado



def leer_dni_omr(imagen):
    
    # 2. Escala de grises
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # 3. Desenfoque (Blur) para eliminar ruido del papel
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 4. Umbralización (Threshold)
    # THRESH_BINARY_INV convierte lo oscuro (lápiz) en blanco y el papel en negro.
    # Otsu encuentra el umbral óptimo automáticamente.
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    return imagen, thresh



def procesar_cuadricula(thresh_image, num_digitos=6, opciones=10):
    # Obtenemos las dimensiones de la imagen recortada
    altura, ancho = thresh_image.shape
    
    # Calculamos el tamaño de cada celda individual
    ancho_celda = ancho // num_digitos
    alto_celda = altura // opciones
    
    dni_detectado = ""
    
    # Recorremos cada columna (cada dígito del DNI)
    for j in range(num_digitos):
        fila_mas_marcada = -1
        max_pixeles = -1
        
        # Empezamos en x para esta columna
        start_x = j * ancho_celda
        end_x = (j + 1) * ancho_celda
        
        # Recorremos las 10 opciones (0-9) hacia abajo
        for i in range(opciones):
            start_y = i * alto_celda
            end_y = (i + 1) * alto_celda
            
            # Recortamos esa celda específica (ROI - Region of Interest)
            celda = thresh_image[start_y:end_y, start_x:end_x]
            
            # CONTAMOS PÍXELES NO CERO (Blancos)
            # Esto nos dice cuánta "tinta" hay en la casilla
            total_pixeles = cv2.countNonZero(celda)
            
            # Si esta celda tiene más tinta que la anterior récord, es la ganadora
            if total_pixeles > max_pixeles:
                max_pixeles = total_pixeles
                fila_mas_marcada = i
        
        # Añadimos el número ganador al resultado
        dni_detectado += str(fila_mas_marcada)
        
    return dni_detectado



# --- FUNCIÓN AUXILIAR PARA ORDENAR ---
def ordenar_contornos(cnts, metodo="left-to-right"):
    # Inicializar las coordenadas inversas y el índice
    reverse = False
    i = 0
    # Si es de arriba/abajo, ordenamos por la coordenada Y (índice 1)
    # Si es izquierda/derecha, ordenamos por la coordenada X (índice 0)
    if metodo == "top-to-bottom" or metodo == "bottom-to-top":
        i = 1
    if metodo == "bottom-to-top" or metodo == "right-to-left":
        reverse = True

    # Crear una lista de bounding boxes y ordenarlas junto con los contornos
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
        key=lambda b: b[1][i], reverse=reverse))
    return (cnts, boundingBoxes)
# -------------------------------------




# --- NUEVA FUNCIÓN PRINCIPAL DE LECTURA ---
def detectar_resultado_omr(imagen_thresh):
    """
    Toma la imagen binaria (thresh) y devuelve el número detectado.
    Asume 10 filas (dígitos 0-9) y columnas variables.
    """

    # 1. Encontrar contornos en la imagen binaria
    cnts = cv2.findContours(imagen_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1] # Compatibilidad entre versiones de OpenCV

    print(f"Numero de cajas: {len(cnts)}")

    cajas_cnts = []

    # 2. Filtrar contornos para quedarse solo con las casillas cuadradas
    # IMPORTANTE: Ajusta 'min_size' si tus cajas son más pequeñas o más grandes en píxeles.
    min_size = 3
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h) # Relación de aspecto

        # Filtro: deben ser suficientemente grandes y aproximadamente cuadradas (ar entre 0.8 y 1.2)
        if w >= min_size and h >= min_size and ar >= 0.8 and ar <= 1.2:
            cajas_cnts.append(c)

    if len(cajas_cnts) == 0:
        return "Error: No se detectaron cajas"
    
    print(f"Numero de cajas: {len(cajas_cnts)}")

    # 3. Ordenar contornos globalmente de Arriba a Abajo para separar por filas
    cajas_cnts = ordenar_contornos(cajas_cnts, metodo="top-to-bottom")[0]

    # Asumimos que siempre hay 10 filas (para los dígitos del 0 al 9)
    filas_esperadas = 10
    total_cajas = len(cajas_cnts)
    cols_esperadas = total_cajas // filas_esperadas

    resultados_detectados = []

    # 4. Iterar por bloques de filas
    # Usamos np.arange para saltar de fila en fila (ej: 0, 8, 16... si hay 8 columnas)
    for (fila_idx, i) in enumerate(np.arange(0, total_cajas, cols_esperadas)):
        # Extraer los contornos de la fila actual
        cnts_fila_actual = cajas_cnts[i : i + cols_esperadas]

        # IMPORTANTE: Ordenar esta fila de Izquierda a Derecha
        cnts_fila_actual = ordenar_contornos(cnts_fila_actual, metodo="left-to-right")[0]

        # Iterar sobre cada caja de la fila actual
        for (col_idx, c) in enumerate(cnts_fila_actual):
            # Crear una máscara para esta caja específica
            mask = np.zeros(imagen_thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            # Aplicar la máscara y contar píxeles blancos
            mask = cv2.bitwise_and(imagen_thresh, imagen_thresh, mask=mask)
            total_pixeles_blancos = cv2.countNonZero(mask)

            # --- LÓGICA DE DECISIÓN ---
            # Calculamos el área total de la caja para sacar un porcentaje de relleno
            (_, _, w_box, h_box) = cv2.boundingRect(c)
            area_total = w_box * h_box
            porcentaje_relleno = total_pixeles_blancos / float(area_total + 0.01) # +0.01 evita div por cero

            # UMBRAL: Si más del 50% (0.5) es blanco, consideramos que está marcada.
            # Una caja vacía solo tiene el borde blanco (quizás un 20-30% de blanco).
            # Una caja rellena debería tener más del 70-80% de blanco. 0.5 es un punto medio seguro.
            if porcentaje_relleno > 0.5:
                valor_digito = fila_idx  # La fila 0 es el dígito 0, la fila 9 es el dígito 9
                # Guardamos tupla: (posición_columna, valor_detectado)
                resultados_detectados.append((col_idx, valor_digito))

    # 5. Reconstruir el número final
    # Ordenamos los resultados por su índice de columna para ponerlos en orden
    resultados_detectados.sort(key=lambda x: x[0])

    # Unimos los valores detectados
    numero_final_str = "".join([str(val) for (col, val) in resultados_detectados])

    if not numero_final_str:
        return "No se detectó ningún número marcado"

    return numero_final_str






RutaPDF = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Numero_Cuadricula\Epson_05112025111319(1)_Censurado.pdf"
RutaImagenDestino = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas"

Imagen = Cargar_Paginas_PDF(RutaPDF)

CoordenadasROI = DimensionesROI(x = 387, y = 135, ancho = 110, alto = 170)

Recorte = Extraer_ROI_Iamgen(Imagen, CoordenadasROI)

Recorte, Recorte_procesado = leer_dni_omr(Recorte)

cv2.imwrite(os.path.join(RutaImagenDestino, rf"PruebaCuadricula.jpg"), Recorte)
cv2.imwrite(os.path.join(RutaImagenDestino, rf"PruebaCuadriculaProcesada.jpg"), Recorte_procesado)

# num_mat = procesar_cuadricula(Recorte_procesado)
num_mat = detectar_resultado_omr(Recorte_procesado)

print(f"El Numero de Matricula detectado es: {num_mat}")


# --- USO DEL CÓDIGO ---
# img_original, img_procesada = leer_dni_omr('recorte_dni.jpg')
# dni = procesar_cuadricula(img_procesada)
# print(f"El DNI detectado es: {dni}")
