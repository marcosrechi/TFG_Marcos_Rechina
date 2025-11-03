import cv2
import numpy as np
from pdf2image import convert_from_path
import os

def Cargar_Imagen(RutaPDF):
    
    if not os.path.exists(RutaPDF, dpi=300):
        print(f"ERROR: La imagen de la ruta {RutaPDF} no existe")
        return None
    
    print(f"Conviertiendo Pdf {RutaPDF} a imagenes")
    Imagenes = convert_from_path(RutaPDF, dpi=dpi)
    if Imagen is None:
        print(f"ERROR: No se pudo cargar la imagen de la ruta {RutaImagen}")
        return None
    
    print(f"Imagen cargada con exito: {Imagen.shape}")
    return Imagen



def main():

    RutaPDF = "C:\Users\marco\Documents\00 OneDriveSync\03 Educacion\03 Universidad\02 Ingenieria Electronica\03 TFG\test 7seg Epson_19092025163133 pag1.pdf"

    Imagen = Cargar_Imagen(RutaImagen)


if __name__ == "__main__":
    main()