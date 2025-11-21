# import cv2
# import pytesseract
# import matplotlib.pyplot as plt

# # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# image = cv2.imread(r"C:\Users\Usuario\Documents\___Pruebas\Zona7segmentos.jpg")
# height, width = image.shape[:2]

# # roi = image[70:100, 450:530]

# roi = image[130:180, 50:530]

# scale_factor = 3
# roi = cv2.resize(roi,
#                  None,
#                  fx = scale_factor,
#                  fy = scale_factor,
#                  interpolation=cv2.INTER_CUBIC)

# cv2.imwrite(r"C:\Users\Usuario\Documents\___Pruebas\Zona7segmentos_Ampliada.jpg", roi)

# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# _, thresh = cv2.threshold(gray, 140, 255,
#                           cv2.THRESH_BINARY_INV)

# text = pytesseract.image_to_string(thresh)

# print(f"Este es el resultado del OCR: {text}")



import numpy as np
import cv2
# import imutils
from skimage import exposure
from pytesseract import image_to_string
import PIL


def process_image(orig_image_arr):

  gry_disp_arr = cv2.cvtColor(orig_image_arr, cv2.COLOR_BGR2GRAY)
  gry_disp_arr = exposure.rescale_intensity(gry_disp_arr, out_range= (0,255))

  #thresholding
  ret, thresh = cv2.threshold(gry_disp_arr,0,255,cv2.THRESH_BINARY)
  
  return thresh

def ocr_image(orig_image_arr):
  otsu_thresh_image = process_image(orig_image_arr)
  # cv2_imshow(otsu_thresh_image)
  return image_to_string(otsu_thresh_image, lang="letsgodigital", config="--psm 8 -c tessedit_char_whitelist=.0123456789")

img1 = cv2.imread(r"C:\Users\Usuario\Documents\___Pruebas\Zona7segmentos.jpg")
cnv = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
text = ocr_image(cnv)

