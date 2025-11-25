# 🧱 Proyecto Data Science: Optimización de Inventario y Segmentación de Clientes

## 💡 Resumen Ejecutivo

Este proyecto aplica técnicas de Machine Learning para resolver dos desafíos críticos de negocio en el sector de materiales de construcción (retail): **la ineficiencia en la gestión de inventario** y la **segmentación imprecisa de clientes**.

Se desarrollaron dos modelos independientes—un Regresor de Series Temporales y un Cluster K-Means/RFM—desplegados en una aplicación interactiva con **Streamlit** para la toma de decisiones proactiva.

---

## 🎯 Objetivos Principales

| Objetivo de Negocio | Solución ML | Valor Estratégico |
| :--- | :--- | :--- |
| **Optimizar Inventario** | Predicción de Demanda (Gradient Boosting) | Reducir el *overstock* y prevenir el *stockout* en productos clave (Principio de Pareto). |
| **Focalizar Marketing** | Segmentación RFM + K-Means | Identificar clientes VIP, en riesgo y dormidos, permitiendo campañas de retención y reactivación precisas. |
| **Democratizar Datos** | Aplicación Streamlit | Poner el poder predictivo directamente en manos de los equipos de Compras y Marketing. |

---

## 💻 Arquitectura y Metodología Técnica

El proyecto sigue un pipeline riguroso (ver notebooks `01_limpieza.ipynb` a `03_entrenamiento_evaluacion.ipynb`).

### 1. Ingeniería de Datos y Preprocesamiento

1.  **Limpieza:** Manejo de datos semi-estructurados (simulando exportes de ERP), unificación de formatos numéricos y filtrado de transacciones nulas/devueltas.
2.  **Agregación Dual:** Transformación de transacciones a dos datasets clave: **Temporal** (`[ID_Producto, Mes]`) y **Cliente** (`[Cliente]`).
3.  **Normalización:** Uso de `StandardScaler` en las variables RFM para asegurar que el K-Means no sea sesgado por la magnitud de la variable *Monetary*.

### 2. Modelo de Predicción de Demanda (Series Temporales)

* **Enfoque:** Regresión Supervisada sobre Series de Tiempo.
* **Feature Engineering:** Creación de variables de **Lags** ($t-1, t-2, t-12$) para capturar la autocorrelación reciente y la estacionalidad anual.
* **Torneo de Modelos:** Benchmarking de 5 modelos (Linear, Ridge, Random Forest, etc.) utilizando **Validación Cruzada Temporal** (`TimeSeriesSplit`).
* **Modelo Seleccionado:** **Gradient Boosting Regressor** (o Random Forest), seleccionado por su capacidad de manejar relaciones no lineales y el mejor rendimiento R².

### 3. Modelo de Segmentación (RFM + Híbrido)

* **Base:** Cálculo de métricas **Recencia, Frecuencia, y Monetario (RFM)**. 
* **Pre-Filtro:** Clientes con `Recency > 365 días` son clasificados como Inactivos **antes** del clustering para maximizar la calidad de los grupos activos.
* **Clustering:** **K-Means** para identificar patrones de comportamiento.
* **Etiquetado de Negocio:** Aplicación de una lógica híbrida usando los **Cuartiles (Q1, Q3)** de la variable *Monetary* para asignar etiquetas operativas (`VIP`, `Regular`, `Dormido`).

---

## 🚀 Despliegue y Uso (Streamlit App)

El proyecto se despliega como una aplicación web interactiva usando Streamlit.

### Estructura de la Aplicación:

1.  **Dashboard de Inventario:** Permite seleccionar un producto clave (Top 20%) y muestra la **proyección de demanda** a 6 o 12 meses, facilitando la planificación de compras.
2.  **Clasificador de Clientes:** Permite ingresar un `ClienteID` y sus métricas RFM, y el modelo devuelve instantáneamente su **segmento de negocio** y la acción de marketing recomendada.

### Requisitos

Para ejecutar la aplicación localmente, necesita:

```bash
pip install pandas scikit-learn seaborn matplotlib streamlit joblib

## 👤 Contacto

Este proyecto fue desarrollado por **José Miguel Benegas Barua**.  

🔗 **LinkedIn:** [https://www.linkedin.com/in/jos%C3%A9-benegas-barua-b7118223a/]
📧 **Correo:** [jose.baruabenehas@gmail,com]





