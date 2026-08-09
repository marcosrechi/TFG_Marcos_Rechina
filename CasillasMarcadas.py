# Para la lectura y rasterización de páginas de documentos PDF
import fitz # Para abrirlo simplemente no necesitas fitz, pero si quieres coger las imagenes y trabajar con ellas etc etc si te hace falta 

# Para el procesamiento de imágenes y operaciones de visión artificial
import cv2

# Para el manejo de matrices, arrays multidimensionales y cálculo de densidad
import numpy as np

# Para la gestión de rutas y verificación en el sistema de archivos
import os


# Establecemos una clase para las dimensiones / coordenadas del recorte 
class DimensionesROI:
    def __init__(self, x, y, ancho, alto):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

# Función que se llama desde el otro script para realizar el proceso de extracción de matrícula
def extraer_numero_matricula(ruta_pdf):

    # Aqui cargo la primera página del PDF como imagen 
    imagen = cargar_paginas_pdf(ruta_pdf)

    # Si hubo un error al cargar la imagen, devuelvo un string "XXXXXX" (que es lo que espera el módulo principal en caso de error)
    if imagen is None:
        return "XXXXXX"

    # Estas son las coordenadas del PDF original donde se encuentra la cuadrícula (con un margen alto por si en el escaneo no se encuentra siempre exactamente en el mismo lugar)
    coordenadas_base = DimensionesROI(x = 387, y = 135, ancho = 110, alto = 170)

    # Aqui lo escalamos para ajustar las coordenadas al pixmap
    dpi = 150
    factor_escala = dpi / 72.0
    coordenadas_roi = DimensionesROI(
        x=int(coordenadas_base.x * factor_escala),
        y=int(coordenadas_base.y * factor_escala),
        ancho=int(coordenadas_base.ancho * factor_escala),
        alto=int(coordenadas_base.alto * factor_escala)
    )

    # Aquí recorto de la primera página solo la zona donde se encuentra la cuadrícula
    recorte = extraer_roi_imagen(imagen, coordenadas_roi)

    # Si hubo un error al recortar la imagen, devuelvo un string "XXXXXX" (que es lo que espera el módulo principal en caso de error)
    if recorte is None or recorte.size == 0:
        return "XXXXXX"

    # Aquí proceso la imagen para poder reconocer que casillas son las que están marcadas
    _, _, recorte_final = procesar_imagen(recorte)

    # Aquí mando el recorte ya procesado para detectar que casillas están marcadas
    numero_matricula = detectar_resultado_omr(recorte_final)

    # Devuelvo el número de matrícula (como una variable tipo str, no un entero)
    return numero_matricula

# Esta función se encarga de guardar la primera página del PDF que le des en una variable cv2
def cargar_paginas_pdf(rutapdf, dpi = 150):

    # Inicializo la variable
    imagen_cv2 = None

    try:
        with fitz.open(rutapdf) as doc:
            
            # Escogemos la primera página del pdf (donde estaría la cuadrícula)
            pagina = doc[0]

            # Creo una matriz de la imagen para poder aumentar el tamaño de esta.
            # Cuanto mas grande es el dpi, más grande y nítida la imagen, pero más ocupará en la memoria
            matriz = fitz.Matrix(dpi/72, dpi/72)

            # Transforma la imagen en un mapa de píxeles
            # Los PDFs son en verdad "instrucciones" de donde dibujar líneas, puntos, etc.
            # Al transformarlo en mapa de píxeles "ejecutas" esas instrucciones para obtener un mapa de píxeles con colores
            mapa_pixeles = pagina.get_pixmap(matrix=matriz)

            # Aqui se convierte ese mapa de píxeles en una imagen de 3 dimensiones (altura, anchura y color)
            imagen_cv2 = np.frombuffer(mapa_pixeles.samples, dtype=np.uint8).reshape(mapa_pixeles.height, mapa_pixeles.width, mapa_pixeles.n)

            # Paso la imagen a una variable tipo OpenCV para poder trabajar con ella
            # OpenCV trabaja con las imagenes en BGR, por eso el cambio de color
            if mapa_pixeles.n == 4:  # RGBA
                imagen_cv2 = cv2.cvtColor(imagen_cv2, cv2.COLOR_RGBA2BGR)
            else:  # RGB
                imagen_cv2 = cv2.cvtColor(imagen_cv2, cv2.COLOR_RGB2BGR)
            
    except Exception as e:
        print(f"Error leyendo el PDF: {e}")
        return None

    # Devuelvo la primera página del PDF ya retocada y como archivo cv2
    return imagen_cv2

# Esta función simplemente recorta una imagen con unas coordenadas dadas
def extraer_roi_imagen(imagen, coordenadas):

    recorte = imagen[coordenadas.y : coordenadas.y + coordenadas.alto, coordenadas.x : coordenadas.x + coordenadas.ancho]

    return recorte

# Esta función se encarga de procesar la imagen para poder reconocer que casillas están marcadas
def procesar_imagen(imagen):
    
    # Transformamos la imagen a escala de grises para trabajar más fácil con ella (el color en este caso no nos importa)
    imagen_grises = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # Aquí se aplica un filtro (desenfoque) con el que se difumina el ruido de papel y se puede eliminar (polvo, arrrugas del papel, etc.)
    imagen_sin_ruido = cv2.GaussianBlur(imagen_grises, (5, 5), 0)
    
    # 4. Umbralización (Threshold)
    # THRESH_BINARY_INV convierte lo oscuro (lápiz) en blanco y el papel en negro.
    # Otsu encuentra el umbral óptimo automáticamente.

    # Esta función "polariza" la imagen. Todo por encima de un umbral se le aplica un valor, todo por debajo se queda en 0
        # "imagen_sin_ruido" es la imagen de entrada
        # 0 es el valor del umbral (no nos importa este valor, se ignorará)
        # 255 es el valor que se le aplicará a lo que supere el umbral
        # "cv2.THRESH_BINARY_INV" invierte los colores de la imagen (es más fácil trabajar con líneas blancas en fondo negro que al revés)
        # "cv2.THRESH_OTSU" analiza la imagen y establece el umbral de manera inteligente para que se separe el fondo del papel de la tinta
        # "threshold" devuelve primero el umbral y luego la imagen procesada, por eso el [1]
    imagen_umbral = cv2.threshold(imagen_sin_ruido, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Esta función se encarga de eliminar las lineas horizontales que tienen los exámenes por norma debajo de la primera fila
    imagen_umbral_sin_linea = eliminar_linea_horizontal(imagen_umbral)
    
    return imagen, imagen_umbral, imagen_umbral_sin_linea

# Esta función se encarga de eliminar la línea que se encuentra debajo de la primera fila de cajas
def eliminar_linea_horizontal(imagen_umbral):

    # Primero creamos un elemento que sea una fina línea horizontal
    # Este es el ancho de la línea elegido (ya que el tamaño mínimo de la caja la establecemos en 10 (más adelante), el ancho lo ponemos en más del doble para que no detecte cajas, solo la línea en cuestión)
    ancho_linea_horizontal_tipo = 30

    # "cv2.MORPH_RECT" hace que tenga la forma de rectángulo
    # "cv2.getStructuringElement" crea el objeto
    linea_horizontal_tipo = cv2.getStructuringElement(cv2.MORPH_RECT, (ancho_linea_horizontal_tipo, 1))

    # Aquí se filtra y se eliminan todas las líneas, cuyo ancho sea más pequeño que el ancho de "linea_horizontal_tipo", quedando solo la línea larga guardándolo en la máscara
    # Como las cajas medirán 10-15 se eliminará todo menos la línea horizontal grande
    mascara_linea = cv2.morphologyEx(imagen_umbral, cv2.MORPH_OPEN, linea_horizontal_tipo)

    # Aquí ampliamos la máscara verticalmente, para asegurarnos de que se elimine por completo y no solo haga la línea máas fina
    # Esto se hace pasando una línea de 2 píxeles de alto y 1 de ancho por los bordes de la línea aumentándolo los píxeles verticales de la máscara
    kernel_dilatacion = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2)) # 2px de alto
    mascara_linea = cv2.dilate(mascara_linea, kernel_dilatacion, iterations=2)

    # Aquí invertimos la máscara para poder trabajar más fácil con ella.
    # Lo blanco se vuelve negro, lo negro se vuelve blanco
    mascara_linea_inv = cv2.bitwise_not(mascara_linea)

    # Aquí hacemos una "resta" de píxeles. Solo se guardan los píxeles que sean blancos en ambas variables
        # La cuadrícula sería fondo negro líneas blancas
        # La máscara sería fondo blanco líneas negras
    # Básicamente pasarían las líneas de la cuadrícula (líneas blancas) NO se encuentren en la línea de la máscara, que se encuentran en el fondo de la máscara (fondo blanco)
    imagen_sin_linea = cv2.bitwise_and(imagen_umbral, imagen_umbral, mask=mascara_linea_inv)

    # Devolvemos la imagen sinn la línea horizontal
    return imagen_sin_linea

# Función encargada de devolver el número detectado tomando la imagen binaria (bresh)
# Asume 10 filas (0-9) y columnas variables
def detectar_resultado_omr(imagen_umbral):

    # Primero encuentro todas las cajas y contornos dentro de la imagen ya tratada

    # La función devuelve los siguientes datos (depende de la versión los datos que devuelve "findContours" son diferentes)
    # v1: (imagen_modificada, contornos, jerarquia)
    # v2: (contornos, jerarquia)
    lista_contornos = cv2.findContours(imagen_umbral.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # De los datos me guardo solo los contornos (esto asegura la compatibilidad entre versiones)
    lista_contornos = lista_contornos[0] if len(lista_contornos) == 2 else lista_contornos[1]

    # Inicializo la lista de cajas finales
    lista_cajas = []

    # Establezo un filtro para las cajaas obtenidas, poniendo un mínimo de tamaño y de relación entre largo y ancho ("rel_ancho_altura" entre 0.5 y 1.5)
    tamanho_minimo = 10
    for c in lista_contornos:

        # Obtendo todos los datos de la caja
        (x, y, w, h) = cv2.boundingRect(c)

        # Calculo la relación de aspecto
        rel_ancho_altura = w / float(h)

        # Si la caja pasa el filtro, se añade en la lista final
        if w >= tamanho_minimo and h >= tamanho_minimo and rel_ancho_altura >= 0.5 and rel_ancho_altura <= 1.5:
            lista_cajas.append(c)

    # Si la lista final está vacía, se devuelve el error
    if len(lista_cajas) == 0:
        # print("Error: No se detectaron cajas")
        return "XXXXXX"


    # Después obtengo cuantas columnas hay en base a las columnas de la primera fila

    # Obtengo una lista de todos los datos (x, y, w, h) de las cajas que han pasado el filtro
    lista_cuadrados = [cv2.boundingRect(c) for c in lista_cajas]
    
    # Las ordenamos simplemente por altura (valor y, [1] de lista_cuadrados)
    lista_cuadrados_ordenadas_altura = sorted(lista_cuadrados, key=lambda b: b[1])

    # Guardo el valor de la altura de la primera caja de la lista (la más alta) [primera caja][altura]
    altura_inicial = lista_cuadrados_ordenadas_altura[0][1]

    # Establezo una tolerancia (en píxeles) para las cajas de la misma fila
    tolerancia_altura = 8 
    
    # Obtengo las colmunas de la primera fila y las establezco como las columnas esperadas
    # Se suman todas las cajas, en la cual la diferencia entre su altura y la altura de la primera caja esta por debajo del umbral
    columnas_esperadas = sum(1 for b in lista_cuadrados_ordenadas_altura if abs(b[1] - altura_inicial) <= tolerancia_altura)
    
    # El número de filas si que se puede establecer como fijo (hay 10 cifras posibles, del 0-9)
    filas_esperadas = 10

    # Calculo el número de cajas esperado
    total_esperado = filas_esperadas * columnas_esperadas

    # Comparo el número de cajas esperado con el número de cajas obtenido y, si no son iguales, lo marco como error
    if len(lista_cajas) != total_esperado:
        # print(f"Error de consistencia geométrica: Se detectaron {len(lista_cajas)} cajas, pero se esperaban {total_esperado} ({columnas_esperadas} cols x 10 filas).")
        return "XXXXXX"

    # Ordenamos las cajas por altura con la función encargada para ello
    lista_cajas = ordenar_contornos(lista_cajas, metodo="arriba-abajo")[0]

    # Inicializo los resultados a X (si se detecta un número se sobreescribirá el X)
    resultados_detectados = ['X'] * columnas_esperadas


    # Después examinamos una a una las cajas que han pasado el filtro para obtener cuales están marcadas y cuales no

    # Recorro la matriz fila por fila 
    for (fila_idx, i) in enumerate(np.arange(0, len(lista_cajas), columnas_esperadas)):

        # Primero guardo todas las cajas (ya ordenadas por altura) que correspondan a la misma fila
        cajas_fila_actual = lista_cajas[i : i + columnas_esperadas]

        # Ordeno las cajas de la misma fila de izquierda a derecha
        cajas_fila_actual = ordenar_contornos(cajas_fila_actual, metodo="izquierda-derecha")[0]

        # Recorro la lista de cajas de la misma fila columna por columna para examinar cada caja por separado
        for (col_idx, c) in enumerate(cajas_fila_actual):

            # Crea una filtro/máscara - Lienzo de mismo tamaño que "imagen_umbral" lleno de 0 (completamente negro), con posibilidad de valores de 0 a 255 (escala de grises)
            filtro = np.zeros(imagen_umbral.shape, dtype="uint8")

            # Dibuja el contorno de c como blanco (255) - El "-1"  significa grosor negativo. Al poner grosor negativo no solo se dibujan la línea del contorno, si no que se rellena por completo
            cv2.drawContours(filtro, [c], -1, 255, -1)

            # Aplicar la máscara. Solo dejo pasar los bits de la imagen original que se encuentran tambien en la máscara y sobreescribo "mask" con el resultado
            filtro = cv2.bitwise_and(imagen_umbral, imagen_umbral, mask=filtro)

            # Cuento el total de pixeles blancos (en verdad cuenta los píxeles que no son 0, que no son negros)
            total_pixeles_blancos = cv2.countNonZero(filtro)

            # Obtengo el cuadrado mas pequeño posible que rodea el contorno de c, y guardo su altura y anchura
            (_, _, w_caja, h_caja) = cv2.boundingRect(c)

            # Calculo el área del contorno (la total original aprox.)
            area_total = w_caja * h_caja

            # Cálculo el porcentaje de píxeles que no son blancos en relación al área original
            porcentaje_relleno = total_pixeles_blancos / float(area_total + 0.01) # +0.01 evita div por cero

            # Si el porcentaje es mayor a 60%, lo consideramos como válido (ponemos un 0.62 para ser un poco más estrictos)
            # Una caja vacía solo tiene el borde blanco (quizás un 40-50% de blanco, ya que hacemos los bordes más anchos)
            # Una caja rellena debería tener más del 70-80% de blanco. 0.62 consigue que no se den falsos positivos, pero cogiendo todos los posibles marcajes.
            if porcentaje_relleno > 0.62:

                # Si no se han detectado previamente ninguna casilla marcada en esa posición
                if resultados_detectados[col_idx] == "X":

                    # Guardo en la posición de la columna (la columna indica la posición de la cifra) el valor de la fila (la cifra en sí)
                    # Guardo los datos como str para que no haya confusión de tipo de variable con los XXXXXX
                    resultados_detectados[col_idx] = str(fila_idx)
                
                # Si ya se detectó en su momento una casilla marcada en esa posición
                else:

                    # Lanzamoss el error y sobreescribimos esa posición con una M (para diferenciarlo de la X)
                    # print(f"Doble marca detectada en la columna {col_idx} (Fila {resultados_detectados[col_idx]} y Fila {fila_idx})")
                    resultados_detectados[col_idx] = 'M'

    # Guardo todos los números detectados en una misma variable (de tipo str)
    numero_final_str = "".join(resultados_detectados)

    # Devuelvo el número obtenido 
    return numero_final_str

# Función encargada de ordenadar loss contornos (las cajas) con el método que se pida
def ordenar_contornos(contornos, metodo="izquierda-derecha"):

    # Incializamos el sentido y el índice de la variable "contornos" que se usará
    reverse = False     # Sentido normal
    i = 0               # Ordenar por coordenada X

    # Si queremos por altura, cambiamos el índice a 1 (coordenada Y)
    if metodo == "arriba-abajo" or metodo == "abajo-arriba":
        i = 1

    # Si queremos el sentido inverso, establecemos "reverse" como True
    if metodo == "abajo-arriba" or metodo == "derecha-izquierda":
        reverse = True

    # Crear una lista de bounding boxes y ordenarlas junto con los contornos
    # Creamos una lista con los cuadrados que rodean a los contornos (auxiliar para ordenarlo)
    cuadrados_contornos = [cv2.boundingRect(c) for c in contornos]

    # Ordenamos tanto los contornos como los cuadrados, siguiendo 3 pasos:
    # 1. Agrupamos los contornos y los cuadrados (para que se ordenen juntos)
    # 2. Ordenamos los según la siguiente regla (para eso sirve el key):
        # lambda - Para poder escribir una función de manera "rápida" (anónima)
        # [1] - Ordenamos según los cuadrados, no los contornos
        # [i] - Ordenamos según la coordenada X o Y, depende de lo que se haya elegido
        # reverse - Hazlo en orden inverso o no, depende de lo que se haya elegido
    # 3. Desagrupamos los contornos y los cuadrados para guardarlos en sus respectivas variables
    (contornos, cuadrados_contornos) = zip(*sorted(zip(contornos, cuadrados_contornos), key=lambda b: b[1][i], reverse=reverse))

    # Devolvemos tanto los contornos como los cuadrados ordenados (en un princpio usaremos más adelante solo la lista de contornos)
    return (contornos, cuadrados_contornos)



# Main encargado de hacer pruebas de solo este script (No se usa en la aplicación final)
def main():

    rutapdf = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Numero_Cuadricula\Epson_05112025111319(1)_Censurado.pdf"
    RutaimagenDestino = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\Fotos Pruebas"

    imagen = cargar_paginas_pdf(rutapdf)

    coordenadas_base = DimensionesROI(x = 387, y = 135, ancho = 110, alto = 170)

    dpi = 150
    factor_escala = dpi / 72.0
    coordenadas_roi = DimensionesROI(
        x=int(coordenadas_base.x * factor_escala),
        y=int(coordenadas_base.y * factor_escala),
        ancho=int(coordenadas_base.ancho * factor_escala),
        alto=int(coordenadas_base.alto * factor_escala)
    )

    recorte = extraer_roi_imagen(imagen, coordenadas_roi)

    recorte, recorte_procesado, recorte_procesado_sin_linea = procesar_imagen(recorte)

    cv2.imwrite(os.path.join(RutaimagenDestino, rf"PruebaCuadricula.jpg"), recorte)
    cv2.imwrite(os.path.join(RutaimagenDestino, rf"PruebaCuadriculaProcesada.jpg"), recorte_procesado)
    cv2.imwrite(os.path.join(RutaimagenDestino, rf"PruebaCuadriculaProcesadaCambiada.jpg"), recorte_procesado_sin_linea)


    num_mat = detectar_resultado_omr(recorte_procesado_sin_linea)
    print(f"El Numero de Matricula detectado es: {num_mat}")

    # print(extraer_numero_matricula(rutapdf))


if __name__ == "__main__":
    main()
