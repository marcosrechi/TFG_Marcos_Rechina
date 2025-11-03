import cv2
import numpy as np
import pytesseract
from PIL import Image

from pdf2image import convert_from_path
import os

def Cargar_Imagenes_PDF(RutaPDF, dpi = 300):
    
    if not os.path.exists(RutaPDF):
        print(f"ERROR: La imagen de la ruta {RutaPDF} no existe")
        return None
    
    print(f"Conviertiendo Pdf {RutaPDF} a imagenes")
    Imagenes = convert_from_path(RutaPDF, dpi = dpi)

    if Imagenes is None:
        print(f"ERROR: No se pudo cargar las imagenes de la ruta {RutaPDF}")
        return None

    print(f"Convertidas {len(Imagenes)} imagenes")
    return Imagenes

def Extraer_ROI_Iamgen(Imagen, Coordenadas):




def main():

    RutaPDF = "C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\test 7seg Epson_19092025163133 pag1.pdf"

    Imagenes = Cargar_Imagenes_PDF(RutaPDF)

    CoordenadasROI = (100, 100, 300, 400) # x, y, ancho, alto

    Extraer_ROI_Iamgen(Imagenes[0], CoordenadasROI)


if __name__ == "__main__":
    main()