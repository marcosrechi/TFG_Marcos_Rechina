# Gestor de Exámenes 🎓

Prueba de concepto para la automatización, digitalización y trazabilidad en la gestión de exámenes presenciales (ETSIDI - UPM).

El sistema monitoriza un directorio local en tiempo real, extrae el número de matrícula del alumnado mediante un motor OMR propio basado en OpenCV, actualiza los listados de clase (CSV/JSON), genera un registro de incidencias y envía justificantes de entrega automáticos vía correo electrónico (SMTP).

---

## 🚀 Uso Rápido (Modo Usuario)

Si solo deseas ejecutar la aplicación sin entorno de desarrollo:
1. Ve a la carpeta `dist/` (o compila ejecutando `CrearEjecutable.bat`).
2. Ejecuta **`GestorExamenes.exe`**.

---

## 🛠️ Configuración para Desarrollo

Para modificar o depurar el código fuente:

### 1. Requisitos
* Python 3.10 o superior.

### 2. Instalación de dependencias
Abre la terminal en la carpeta raíz del proyecto y ejecuta:

pip install -r requirements.txt