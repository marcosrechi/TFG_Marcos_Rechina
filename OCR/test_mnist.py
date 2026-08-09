from tensorflow.keras.models import load_model
# from tensorflow.keras.datasets import mnist
import numpy as np
import requests
from PIL import Image

# Paso 1: Descargar el modelo desde GitHub
url = "https://github.com/R4F405/Reconocimiento-de-Digitos-MNIST/raw/main/modelo_mnist.keras"
model_filename = "modelo_mnist.keras"

print("Descargando modelo...")
response = requests.get(url)
with open(model_filename, "wb") as f:
    f.write(response.content)
print("Modelo descargado exitosamente.")

# Paso 2: Cargar el modelo
modelo = load_model(model_filename)
print("Modelo cargado correctamente.")

# Paso 3: Cargar el dataset MNIST para obtener una imagen de prueba
# (_, _), (x_test, y_test) = mnist.load_data()

# Seleccionar una imagen aleatoria
# idx = np.random.randint(0, len(x_test))
# imagen = x_test[idx]
# label_real = y_test[idx]

# 1) Cargar la imagen desde el fichero y convertir a escala de grises
ruta = "Cifra_3_Esperado_8_Obtenido_2_Tesseract_inv.png"
img = Image.open(ruta).convert("L")      # 'L' = escala de grises
img = img.resize((28, 28))               # (opcional) asegurar 28x28 si no lo fuese

# 2) Convertir a numpy y comprobar formato
imagen = np.array(img, dtype=np.uint8)   # -> shape (28, 28), valores 0–255

# 3) Preprocesar igual que con MNIST
imagen_normalizada = imagen / 255.0
imagen_entrada = imagen_normalizada.reshape(1, 28, 28, 1)

# Ahora se guarda la imagen procesada para referencia
img_procesada = Image.fromarray((imagen_entrada[0, :, :, 0] * 255).astype(np.uint8))
img_procesada.save("imagen_procesada.png")

# Paso 4: Realizar la predicción
prediccion = modelo.predict(imagen_entrada)
numero_predicho = np.argmax(prediccion)

# print(f"Etiqueta real: {label_real}")
print(f"Número predicho por el modelo: {numero_predicho}")