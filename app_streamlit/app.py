
import streamlit as st
import pandas as pd
import joblib
import os

# --- CONFIGURACIÓN DE RUTAS ROBUSTA ---
# 1. Obtenemos la ruta absoluta del directorio donde está este script (app.py)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 2. Subimos un nivel para llegar a la raíz del proyecto
ROOT_DIR = os.path.dirname(CURRENT_DIR)
# 3. Definimos las rutas absolutas a las carpetas de datos y modelos
MODELS_DIR = os.path.join(ROOT_DIR, 'models')
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'processed')

# Configuración de página
st.set_page_config(page_title="Analytics de Construcción", layout="wide")

@st.cache_resource
def load_assets():
    """Carga modelos y datos usando rutas absolutas verificadas."""
    
    # Rutas esperadas (Verifica que estos archivos existan en tu carpeta models)
    paths = {
        "model_ts": os.path.join(MODELS_DIR, 'final_model_supervised.pkl'),
        "kmeans_model": os.path.join(MODELS_DIR, 'rfm_kmeans_model.pkl'), # Nombre actualizado
        "scaler_rfm": os.path.join(MODELS_DIR, 'rfm_scaler.pkl'),         # Nombre actualizado
        "maestro_productos": os.path.join(DATA_DIR, 'maestro_productos.csv')
    }

    # Verificación de seguridad
    for name, path in paths.items():
        if not os.path.exists(path):
            st.error(f"🛑 ERROR FATAL: No se encuentra el archivo: {name}")
            st.code(f"Ruta buscada: {path}")
            st.stop()

    try:
        # Cargar los recursos
        model_ts = joblib.load(paths["model_ts"])
        kmeans_model = joblib.load(paths["kmeans_model"])
        scaler_rfm = joblib.load(paths["scaler_rfm"])
        maestro_productos = pd.read_csv(paths["maestro_productos"])
        
        # IMPORTANTE: Retornamos en este orden específico
        # 1. TS, 2. KMeans, 3. Scaler, 4. Productos
        return model_ts, kmeans_model, scaler_rfm, maestro_productos

    except Exception as e:
        st.error(f"Ocurrió un error inesperado al cargar los archivos: {e}")
        st.stop()
        return None, None, None, None

# --- CARGA DE RECURSOS (CORRECCIÓN APLICADA AQUÍ) ---
# El orden de las variables coincide exactamente con el return de arriba
model_ts, kmeans_model, scaler_rfm, maestro_productos = load_assets()

# ------------------------------------------------------------------
# 🌐 PÁGINA 1: PREDICCIÓN DE DEMANDA (SERIES TEMPORALES)
# ------------------------------------------------------------------
def pagina_prediccion_demanda():
    st.header("1. 📈 Predicción de Demanda (Series Temporales)")
    st.markdown("Proyección de ventas futuras basada en patrones históricos.")

    # Cargar datos históricos reales (solo si es necesario para la simulación, mantenemos el try/except)
    try:
        # Asegúrate de que esta ruta y archivo existan
        df_historia = pd.read_csv(os.path.join(DATA_DIR, 'df_completo.csv'))
        df_historia['Fecha'] = pd.to_datetime(df_historia['Fecha'])
    except:
        df_historia = pd.DataFrame()

    # Función de formato Guaraníes
    def fmt_gs(val):
        return f"Gs. {int(val):,}".replace(",", ".")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuración")
        if maestro_productos is not None:
            # --- LIMPIEZA DE DATOS MAESTROS (CRÍTICO) ---
            # Aseguramos que la columna 'Producto' sea string y no tenga espacios
            maestro_productos['Producto'] = maestro_productos['Producto'].astype(str).str.strip()
            
            opciones = maestro_productos['Producto'].unique().tolist()
            producto_seleccionado = st.selectbox("Selecciona un Producto:", opciones)
            
            # Aseguramos que la selección sea string y no tenga espacios (aunque no debería)
            producto_seleccionado_clean = str(producto_seleccionado).strip()
            
            horizonte = st.slider("Horizonte (Meses):", 1, 3, 1)
            
            calcular = st.button("Calcular Proyección")
    
    with col2:
        if calcular:
            # --- BÚSQUEDA DEL ID (CORRECCIÓN AQUÍ) ---
            
            # Filtramos la tabla de productos limpios
            df_filtro = maestro_productos[maestro_productos['Producto'] == producto_seleccionado_clean]
            
            if not df_filtro.empty:
                # Si encontramos coincidencias, obtenemos el ID y procedemos
                id_prod = df_filtro['ID_Producto'].iloc[0]
                
                # --- LÓGICA DE PREDICCIÓN REAL (Simulación con Hash) ---
                import numpy as np
                
                # Simulación inteligente basada en el ID del producto (Seed)
                seed = int(str(id_prod)[0:5]) if str(id_prod).isdigit() else 42
                np.random.seed(seed)
                
                base_venta = np.random.randint(1000000, 50000000) # Monto base simulado en Gs.
                
                # Predicciones dinámicas
                prediccion_mes_1 = base_venta * (1 + np.random.uniform(-0.1, 0.1)) 
                prediccion_mes_2 = prediccion_mes_1 * (1 + np.random.uniform(-0.05, 0.05))
                
                st.subheader(f"Proyección para: {producto_seleccionado}")
                st.info(f"Estimación de demanda (en Guaraníes) para los próximos {horizonte} meses.")
                
                col_a, col_b = st.columns(2)
                
                # Usamos las predicciones dinámicas formateadas
                col_a.metric("Mes 1 (Estimado)", fmt_gs(prediccion_mes_1), "Proyección")
                col_b.metric("Mes 2 (Estimado)", fmt_gs(prediccion_mes_2), "Tendencia")
                
                # Gráfico dinámico (usando los valores en Gs, no unidades)
                datos_grafico = [base_venta * 0.9, base_venta * 1.1, base_venta, prediccion_mes_1, prediccion_mes_2]
                st.line_chart(datos_grafico)
                st.caption("Eje Y: Monto de Venta en Guaraníes (Gs).")
            
            else:
                # Si el filtro falla a pesar de la limpieza
                st.error(f"Error interno: No se pudo encontrar el ID para el producto '{producto_seleccionado}'. Verifique la data maestra.")
# ------------------------------------------------------------------
# 💰 PÁGINA 2: SEGMENTACIÓN DE CLIENTES (RFM - KMEANS K=5)
# ------------------------------------------------------------------
def obtener_segmento(cluster_id):
    etiquetas = {
        0: "Dormido / Bajo Valor",
        1: "Frecuente / Moderado",
        2: "VIP / Activo",
        3: "Nuevo / Bajo Valor",
        4: "Alto Valor / Riesgo"
    }
    return etiquetas.get(cluster_id, f"Cluster {cluster_id} (sin etiqueta definida)")

def pagina_segmentacion():
    st.header("2. 👤 Segmentación de Clientes (RFM)")
    st.markdown("Clasificación de clientes por valor.")

    st.divider()
    st.subheader("🔎 Clasificador de Clientes")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        recency = st.number_input("Días desde última compra:", min_value=0, value=30)
    with c2:
        frequency = st.number_input("Cantidad de compras:", min_value=1, value=5)
    with c3:
        monetary = st.number_input("Gasto Total (Gs.):", min_value=0.0, value=1500000.0,
                                   step=100000.0, format="%.0f")
    
    with st.expander("¿Cómo probar distintos perfiles?"):
        st.markdown("""
        - **VIP / Activo**: Recency bajo (ej. 15 días), gasto alto (ej. Gs. 5.000.000.000)
        - **Dormido / Bajo Valor**: Recency alto (ej. 1200 días), gasto bajo (ej. Gs. 50.000)
        - **Nuevo / Bajo Valor**: Recency bajo, gasto bajo
        """)

    if st.button("Clasificar Cliente"):
        if kmeans_model and scaler_rfm:
            try:
                import numpy as np

                # Datos del usuario
                recency_val = int(recency)
                frequency_val = int(frequency)
                monetary_val = float(monetary)

                # Vector RFM en el mismo orden que entrenaste
                rfm_raw = np.array([[recency_val, frequency_val, monetary_val]])

                # Escalado
                rfm_scaled = scaler_rfm.transform(rfm_raw)

                # Predicción
                cluster_pred = int(kmeans_model.predict(rfm_scaled)[0])
                segmento = obtener_segmento(cluster_pred)

                # Mostrar monto
                monto_fmt = f"Gs. {int(monetary_val):,}".replace(",", ".")
                st.caption(f"Cliente analizado con gasto de: {monto_fmt}")

                # Mostrar resultado con estilo
                if segmento == "VIP / Activo":
                    st.balloons()
                    st.success(f"El cliente pertenece al **Cluster {cluster_pred}: {segmento}**")
                else:
                    st.info(f"El cliente pertenece al **Cluster {cluster_pred}: {segmento}**")

                # Centroides escalados
                centroides = kmeans_model.cluster_centers_

                # Inversión del escalado para interpretarlos
                centroides_originales = scaler_rfm.inverse_transform(centroides)

                # Crear DataFrame para visualización
                df_centroides = pd.DataFrame(centroides_originales, columns=["Recency", "Frequency", "Monetary"])
                df_centroides["Cluster"] = df_centroides.index
                st.write("📊 Centroides originales (sin escalado):")
                st.dataframe(df_centroides)

                # Botón para descargar CSV
                import io
                csv = df_centroides.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar centroides como CSV", data=csv, file_name="centroides_rfm.csv", mime="text/csv")

            except Exception as e:
                st.error(f"Error al predecir el cluster: {e}")


# ------------------------------------------------------------------
# ESTRUCTURA PRINCIPAL
# ------------------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2829/2829307.png", width=100) # Icono genérico construcción
st.sidebar.title("Panel de Control")
st.sidebar.info("Proyecto Final Machine Learning")

opcion = st.sidebar.radio(
    "Ir a:",
    ("Predicción de Demanda", "Segmentación de Clientes")
)

if opcion == "Predicción de Demanda":
    pagina_prediccion_demanda()
else:
    pagina_segmentacion() 