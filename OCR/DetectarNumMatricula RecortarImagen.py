
import fitz
# from pdf2image import convert_from_path

import cv2
import imutils
import numpy as np
from skimage import exposure
import PIL

import os
from PIL import Image
import pytesseract

# Añade esto al inicio de tu código, después de los imports SI NO ESTA AÑADIDO EL PATH A TESSERACT
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



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
    

# def Cargar_Paginas_PDF(RutaPDF, dpi = 300):
    
#     if not os.path.exists(RutaPDF):
#         print(f"ERROR: La imagen de la ruta {RutaPDF} no existe")
#         return None
    
#     print(f"Conviertiendo Pdf {RutaPDF} a imagenes")
#     Paginas = convert_from_path(RutaPDF, dpi = dpi)

#     if Paginas is None:
#         print(f"ERROR: No se pudo cargar las imagenes de la ruta {RutaPDF}")
#         return None

#     print(f"Convertidas {len(Paginas)} paginas")
#     return Paginas

def Extraer_ROI_Iamgen(Imagen, Coordenadas):

    Recorte = Imagen[Coordenadas.y : Coordenadas.y + Coordenadas.alto, Coordenadas.x : Coordenadas.x + Coordenadas.ancho]

    return Recorte

def cnvt_edged_image(img_arr, should_save=False):
  # ratio = img_arr.shape[0] / 300.0
  image = imutils.resize(img_arr,height=300)
  gray_image = cv2.bilateralFilter(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),11, 17, 17)
  edged_image = cv2.Canny(gray_image, 30, 200)

  if should_save:
    cv2.imwrite('cntr_ocr.jpg')

  return edged_image


def find_display_contour(edge_img_arr):
    display_contour = None
    edge_copy = edge_img_arr.copy()
    contours,hierarchy = cv2.findContours(edge_copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    top_cntrs = sorted(contours, key = cv2.contourArea, reverse = True)[:10]

    for cntr in top_cntrs:
        peri = cv2.arcLength(cntr,True)
        approx = cv2.approxPolyDP(cntr, 0.02 * peri, True)

        if len(approx) == 4:
            display_contour = approx
            break

    return display_contour


def crop_display(image_arr):
    edge_image = cnvt_edged_image(image_arr)
    display_contour = find_display_contour(edge_image)
    cntr_pts = display_contour.reshape(4,2)
    return cntr_pts


def normalize_contrs(img,cntr_pts):
    ratio = img.shape[0] / 300.0
    norm_pts = np.zeros((4,2), dtype="float32")

    s = cntr_pts.sum(axis=1)
    norm_pts[0] = cntr_pts[np.argmin(s)]
    norm_pts[2] = cntr_pts[np.argmax(s)]

    d = np.diff(cntr_pts,axis=1)
    norm_pts[1] = cntr_pts[np.argmin(d)]
    norm_pts[3] = cntr_pts[np.argmax(d)]

    norm_pts *= ratio

    (top_left, top_right, bottom_right, bottom_left) = norm_pts

    width1 = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) + ((bottom_right[1] - bottom_left[1]) ** 2))
    width2 = np.sqrt(((top_right[0] - top_left[0]) ** 2) + ((top_right[1] - top_left[1]) ** 2))
    height1 = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
    height2 = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))

    max_width = max(int(width1), int(width2))
    max_height = max(int(height1), int(height2))

    dst = np.array([[0,0], [max_width -1, 0],[max_width -1, max_height -1],[0, max_height-1]], dtype="float32")
    persp_matrix = cv2.getPerspectiveTransform(norm_pts,dst)
    return cv2.warpPerspective(img,persp_matrix,(max_width,max_height))


def process_image(orig_image_arr):
    ratio = orig_image_arr.shape[0] / 300.0

    display_image_arr = normalize_contrs(orig_image_arr,crop_display(orig_image_arr))
    #display image is now segmented.
    gry_disp_arr = cv2.cvtColor(display_image_arr, cv2.COLOR_BGR2GRAY)
    gry_disp_arr = exposure.rescale_intensity(gry_disp_arr, out_range= (0,255))

    #thresholding
    ret, thresh = cv2.threshold(gry_disp_arr,127,255,cv2.THRESH_BINARY)
    return thresh

def ocr_image(orig_image_arr):
    otsu_thresh_image = PIL.Image.fromarray(process_image(orig_image_arr))
    return pytesseract.image_to_string(otsu_thresh_image, lang="letsgodigital", config="-psm 100 -c tessedit_char_whitelist=.0123456789")



def main():

    # Rutas ordenador

    RutaPDF = r"C:\Users\Usuario\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\test 7seg Epson_19092025163133 pag1.pdf"
    
    RutaImagenDestino = r"C:\Users\Usuario\Documents\___Pruebas"

    # Ruta portátil
    # RutaPDF = r"C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\test 7seg Epson_19092025163133 pag1.pdf"
    # RutaImagenDestino = os.path.join(r"C:\Users\marco\Documents\___Pruebas", r"Zona7segmentos.jpg")


    Imagen = Cargar_Paginas_PDF(RutaPDF)
    
    # print(len(Paginas))

    CoordenadasROI = DimensionesROI(x = 445, y = 100, ancho = 85, alto = 30) # x, y, ancho, alto

    Zona7segmentos = Extraer_ROI_Iamgen(Imagen, CoordenadasROI)

    # Guardar la imagen recortada
    cv2.imwrite(os.path.join(RutaImagenDestino, rf"Zona7segmentos.jpg"), Zona7segmentos)

    edge_image = cnvt_edged_image(Zona7segmentos)

    # Guardar la imagen recortada
    cv2.imwrite(os.path.join(RutaImagenDestino, rf"edge_image.jpg"), edge_image)

    crop_image = crop_display(Zona7segmentos)

    # Guardar la imagen recortada
    cv2.imwrite(os.path.join(RutaImagenDestino, rf"crop_image.jpg"), crop_image)


if __name__ == "__main__":
    main()