# 📊 Análisis de Ventas y Crecimiento de Importados

Este proyecto contiene el Análisis Exploratorio de Datos (EDA) completo para diagnosticar los patrones de ventas, crecimiento y estacionalidad de la cartera de productos importados. Se transforma datos de reportes complejos en información clave para la toma de decisiones comerciales.

---

## 🚀 Objetivos del Análisis

El propósito de este EDA es:

* **Limpiar y estructurar** datos complejos de reportes semi-estructurados.
* Identificar el **Top 10 de Productos** más vendidos.
* Diagnosticar el **Crecimiento Interanual Promedio** por grupo de producto.
* Establecer la **Curva de Estacionalidad** mensual para optimizar la planificación de inventarios.
* Evaluar la **Participación y Concentración** de las ventas por grupo (Curva de Pareto).

---

## 🛠️ Cómo Usar y Reproducir el Proyecto

Para ejecutar y replicar el análisis completo, sigue estos pasos:

### 1. Requisitos Previos

* **Python 3.x**
* **Entorno Virtual** (`venv` o `conda`)

### 2. Instalación de Dependencias

Asegúrate de que tu entorno virtual está **activado** y luego instala todas las librerías necesarias especificadas en `requirements.txt`:

```bash
pip install -r requirements.txt

## 🧹 Data Wrangling (Limpieza Robusta)

El proceso de limpieza (detallado en `notebooks/1. limpieza2ipynb`) fue diseñado para manejar la complejidad de los datos:

* **Detección de Jerarquía:** Uso de heurística para separar filas de grupos (encabezados) de filas de productos (detalle de venta) en la columna inicial.  
* **Estandarización Numérica:** Manejo de múltiples formatos de separadores decimales/miles (punto/coma) y paréntesis para negativos.  
* **Fechas:** Parseo robusto para identificar formatos de fecha mixtos (DD/MM/AAAA vs. MM/DD/AAAA).  
* **Filtrado:** Solo se conservan las filas que son de venta/detalle (tienen descripción y algún valor numérico o ID).  

---

## 💡 Hallazgos Clave

🏆 **Concentración de Ventas:**  
El Top 10 de productos/grupos es responsable de una porción significativa del ingreso total (Curva de Pareto).  

📈 **Grupos Dinámicos:**  
Los grupos de producto **[menciona los grupos del top 8 de tu gráfico]** mostraron el mayor crecimiento interanual promedio, señalando áreas con fuerte tracción.  

🕒 **Patrón Estacional:**  
Se observa un claro pico de ventas en **[menciona el mes]** y un valle en **[menciona el mes con menor venta]** al promediar todos los años.  

---

## 👤 Contacto

Este proyecto fue desarrollado por **[Tu Nombre]**.  

🔗 **LinkedIn:** [https://www.linkedin.com/in/jos%C3%A9-benegas-barua-b7118223a/]
📧 **Correo:** [jose.baruabenehas@gmail,com]

---

> **Nota:** Recuerda reemplazar los placeholders entre corchetes `[ ]` con tu información específica y los hallazgos de tu análisis.

