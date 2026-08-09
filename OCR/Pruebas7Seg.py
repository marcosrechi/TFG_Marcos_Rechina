import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import numpy as np
import cv2 # Necesitas instalar esta librería
import os

# --- ⚙️ CONFIGURACIÓN Y VARIABLES ---

# RUTA_CARPETAS = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG"               # Para el portátil
RUTA_CARPETAS = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG"               # Para el ordenador

# 📌 1. Ruta al archivo PDF
# Cambia esto por la ruta real de tu archivo PDF
# ARCHIVO_PDF = r"Numero_7_Segmentos\test 7seg Epson_19092025163133 pag1.pdf"
ARCHIVO_PDF = r"Numero_7_Segmentos\test 7seg Epson_19092025163133 pag2.pdf"

PDF_PATH = os.path.join(RUTA_CARPETAS, ARCHIVO_PDF)


# 📌 2. Coordenadas de la Región de Interés (ROI)
# Las coordenadas son relativas al tamaño original de la página y están en unidades de PDF (puntos).
# Formato: (x0, y0, x1, y1) donde (x0, y0) es la esquina superior izquierda y (x1, y1) es la inferior derecha.
# EJEMPLO DE PRUEBA: Una pequeña región cerca de la esquina superior izquierda (ajusta según tu PDF).
ROI_COORDS = (446, 100, 530, 130)               # Para la cadena entera
# ROI_COORDS = (446, 100, 465, 130)               # Para la cifra 1
# ROI_COORDS = (466, 100, 481, 130)               # Para la cifra 2
# ROI_COORDS = (480, 100, 495, 130)               # Para la cifra 3
# ROI_COORDS = (494, 100, 510, 130)               # Para la cifra 4
# ROI_COORDS = (509, 100, 524, 130)               # Para la cifra 5




# 📌 3. Número de página (empezando desde 0)
PAGE_NUMBER = 0 

# 📌 4. Ruta al ejecutable de Tesseract (¡IMPORTANTE! Descomenta y ajusta si es necesario)
# Si Tesseract no está en el PATH del sistema, debes especificar la ruta exacta.
# Ejemplo en Windows: 
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- 🚀 FUNCIONES PRINCIPALES ---

def extract_region_as_image(pdf_path: str, page_num: int, coords: tuple) -> Image.Image:
    """
    Abre el PDF, navega a la página especificada y extrae la región definida por 
    las coordenadas como una imagen de Pillow (PIL).

    Args:
        pdf_path: Ruta al archivo PDF.
        page_num: Índice de la página (0-basado).
        coords: Tupla (x0, y0, x1, y1) de la región a extraer.

    Returns:
        Un objeto Image de PIL que contiene la región extraída.
    """
    try:
        # Abrir el documento PDF
        document = fitz.open(pdf_path)
        if page_num >= document.page_count:
            raise IndexError(f"La página {page_num} está fuera de rango.")
            
        page = document.load_page(page_num)
        
        # Crear un Rect a partir de las coordenadas
        rect = fitz.Rect(coords)
        
        # Obtener un pixmap (imagen rasterizada) de la región
        # zoom=4.0 aumenta la resolución para un mejor OCR
        matrix = fitz.Matrix(4.0, 4.0) 
        pix = page.get_pixmap(matrix=matrix, clip=rect)
        
        # Convertir el pixmap de PyMuPDF a un objeto Image de PIL
        img_data = pix.tobytes("ppm")
        image = Image.open(io.BytesIO(img_data))
        
        document.close()
        return image
    
    except fitz.FileNotFoundError:
        print(f"ERROR: Archivo no encontrado en la ruta: {pdf_path}")
        raise
    except Exception as e:
        print(f"Error al extraer la imagen del PDF: {e}")
        raise

def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Aplica técnicas de preprocesamiento de imagen para mejorar la precisión del OCR 
    en dígitos de siete segmentos.

    Args:
        image: Objeto Image de PIL de la región extraída.

    Returns:
        Objeto Image de PIL preprocesado.
    """
    
    '''
    # 1. Convertir a escala de grises
    img_gray = image.convert('L')
    
    # 2. Binarización (conversión a blanco y negro puro)
    # El umbral (threshold) debe ajustarse a las características de la imagen. 
    # 180 es un valor común de partida; los píxeles más oscuros que 180 se vuelven negros (0).
    threshold = 180
    img_bin = img_gray.point(lambda p: 0 if p < threshold else 255, '1')
    
    # NOTA: Para dígitos de siete segmentos, la inversión de colores (negro sobre blanco) 
    # a veces es beneficiosa, pero Tesseract suele manejarlo bien. 
    # Si los segmentos son muy delgados, puedes probar técnicas como el engrosamiento.
    
    return img_bin
    '''

    # Segundo intento

    """Aplica preprocesamiento avanzado (Binarización + Dilatación)."""
    
    # 1. Convertir PIL a array de OpenCV (numpy)
    img_np = np.array(image.convert('L'))
    
    # 2. Binarización
    # Convertir a escala de grises y aplicar Binarización Inversa (blanco sobre negro)
    # Tesseract a menudo funciona mejor con texto negro sobre fondo blanco, pero vamos a probar a binarizar normal.
    _, img_bin = cv2.threshold(img_np, 180, 255, cv2.THRESH_BINARY)
    
    # 3. Dilatación (Engrosamiento): Hacer los dígitos más gruesos
    # El kernel define la forma en que se expande el área negra. 
    # Un kernel de 2x2 o 3x3 es suficiente para dígitos finos.
    kernel = np.ones((2, 2), np.uint8)
    img_dilated = cv2.dilate(img_bin, kernel, iterations=1)
    
    # 4. Convertir de vuelta a objeto PIL
    processed_image = Image.fromarray(img_dilated)
    
    return processed_image



def recognize_digit_ocr(image: Image.Image) -> str:
    """
    Realiza el OCR en la imagen preprocesada.

    Args:
        image: Objeto Image de PIL preprocesado.

    Returns:
        El texto reconocido como una cadena de caracteres.
    """
    # Configuración de Tesseract
    # --psm 8: Asume una sola palabra. Ideal para un único dígito. 
    #          Podrías probar --psm 10 (asume un solo caracter) si solo esperas uno.
    # -c tessedit_char_whitelist=0123456789: Restringe la detección solo a dígitos (0-9). 
    #                                         ¡CRUCIAL para dígitos de siete segmentos!
    
    # Para una cifra:
    # ocr_config = r'--psm 10 -c tessedit_char_whitelist=0123456789'
    
    # Para varias cifras
    ocr_config = r'--psm 8 -c tessedit_char_whitelist=0123456789'
    
    # Realizar el OCR
    text = pytesseract.image_to_string(image, lang="letsgodigital", config=ocr_config)
    
    return text.strip()

def sanitize_result(text: str) -> str:
    """
    Limpia el resultado del OCR, eliminando espacios y caracteres no deseados.
    """
    # Eliminar espacios en blanco, saltos de línea y el caracter de nueva página
    sanitized = text.strip().replace('\n', '').replace('\f', '')
    
    # Como ya usamos la whitelist en el OCR, esto es principalmente para asegurar
    # que solo quede el dígito principal.
    if sanitized:
        return sanitized # Tomamos solo el primer caracter si hay varios
    return ""

# --- 🎬 EJECUCIÓN DEL SCRIPT ---

# Variable para almacenar el resultado final
numero_reconocido = ""

try:
    print(f"Iniciando procesamiento del PDF: {PDF_PATH}")
    
    # 1. Extracción de la región
    print(f"Extrayendo región: {ROI_COORDS} de la página {PAGE_NUMBER}...")
    roi_image = extract_region_as_image(PDF_PATH, PAGE_NUMBER, ROI_COORDS)
    
    # Opcional: Guardar la imagen extraída para depuración
    roi_image.save(os.path.join(RUTA_CARPETAS, r"Fotos Pruebas\roi_extraida.png"))
    print("Imagen de la ROI guardada como 'roi_extraida.png' (para depuración).")
    
    # imagen_directa = Image.open(ruta_imagen)

    # 2. Preprocesamiento de la imagen
    print("Preprocesando la imagen (escala de grises, binarización)...")
    processed_image = preprocess_image_for_ocr(roi_image)
    # processed_image = preprocess_image_for_ocr(imagen_directa)
    
    # Opcional: Guardar la imagen preprocesada para depuración
    processed_image.save(os.path.join(RUTA_CARPETAS, r"Fotos Pruebas\roi_preprocesada.png"))
    #  processed_image.save(os.path.join(RUTA_CARPETAS, r"Fotos Pruebas\roi_preprocesada_intento.png"))
    print("Imagen preprocesada guardada como 'roi_preprocesada.png' (para depuración).")

    image_inv = cv2.bitwise_not(np.array(processed_image))
    image_inv_final = Image.fromarray(image_inv)

    image_inv_final.save(os.path.join(RUTA_CARPETAS, r"Fotos Pruebas\roi_preprocesada_inv.png"))
   
    
    # 3. Reconocimiento OCR
    print("Realizando OCR...")
    # raw_result = recognize_digit_ocr(processed_image)
    raw_result = recognize_digit_ocr(image_inv_final)
    
    # 4. Sanitización y almacenamiento
    # numero_reconocido = sanitize_result(raw_result)
    
    sanitized_result = raw_result.strip().replace('\n', '').replace('\f', '')
    
    if sanitized_result:
        # 🚀 MODIFICACIÓN CRUCIAL: Guardamos la cadena completa.
        numero_reconocido = sanitized_result
        print(f"\nResultado OCR en bruto: '{raw_result}'")
    else:
        print("\nOCR no pudo reconocer un dígito en la región.")


    print("\n--- ✅ RESULTADO FINAL ---")
    print(f"Resultado en bruto del OCR: '{raw_result}'")
    print(f"Dígito reconocido y sanitizado: '{numero_reconocido}'")
    
except Exception as e:
    print(f"\n--- ❌ PROCESO FALLIDO ---")
    print(f"Ocurrió un error: {e}")

finally:
    # Mostrar el valor final de la variable
    print(f"\nValor final de 'numero_reconocido': **{numero_reconocido}**")