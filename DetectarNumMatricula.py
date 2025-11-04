# import cv2
# import numpy as np
# import pytesseract
# from PIL import Image

# from pdf2image import convert_from_path
# import os

# import fitz
import numpy as np
from pdf2image import convert_from_path
import cv2
import os
from PIL import Image
import tesseract

class DimensionesROI:
    def __init__(self, x, y, ancho, alto):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto


def Cargar_Paginas_PDF(RutaPDF, dpi = 300):
    
    if not os.path.exists(RutaPDF):
        print(f"ERROR: La imagen de la ruta {RutaPDF} no existe")
        return None
    
    print(f"Conviertiendo Pdf {RutaPDF} a imagenes")
    Paginas = convert_from_path(RutaPDF, dpi = dpi)

    if Paginas is None:
        print(f"ERROR: No se pudo cargar las imagenes de la ruta {RutaPDF}")
        return None

    print(f"Convertidas {len(Paginas)} paginas")
    return Paginas

def Extraer_ROI_Iamgen(Imagen, Coordenadas):

    PaginaCV = cv2.cvtColor(np.array(Imagen), cv2.COLOR_RGB2BGR)

    Recorte = PaginaCV[DimensionesROI.y : DimensionesROI.y + DimensionesROI.alto, DimensionesROI.x : DimensionesROI.x + DimensionesROI.ancho]

    return Recorte



def main():

    RutaPDF = "C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\test 7seg Epson_19092025163133 pag1.pdf"

    Paginas = Cargar_Paginas_PDF(RutaPDF)

    CoordenadasROI = Coordenadas(x = 100, y = 100, ancho = 300, alto = 400) # x, y, ancho, alto

    Zona7segmentos = Extraer_ROI_Iamgen(Paginas[0], CoordenadasROI)


if __name__ == "__main__":
    main()