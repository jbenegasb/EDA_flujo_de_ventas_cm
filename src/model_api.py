# src/model_api.py
import joblib
import pandas as pd

# Define la lista de features que el modelo espera (debe coincidir con tu entrenamiento)
TS_FEATURES = ['Mes', 'Venta_Mes_Ant', 'Venta_2Meses_Ant', 'Venta_Ano_Ant', 'Promedio_Movil_3M']

# --- Funciones de Carga (La app las llamará solo una vez) ---

def cargar_modelos():
    """Carga los modelos entrenados y los scalers del disco."""
    try:
        model_ts = joblib.load('models/final_model_supervised.pkl')
        kmeans_model = joblib.load('models/kmeans_model.pkl')
        scaler_rfm = joblib.load('models/scaler_rfm.pkl')
        return model_ts, kmeans_model, scaler_rfm
    except FileNotFoundError as e:
        print(f"Error cargando modelos: {e}. Asegúrate de que los archivos .pkl existan en la carpeta 'models/'.")
        return None, None, None

# --- Funciones de Predicción ---

def predecir_demanda(modelo_ts, df_futuro):
    """
    Realiza la predicción de demanda para un DataFrame de características futuras.
    'df_futuro' debe tener las columnas definidas en TS_FEATURES.
    """
    if modelo_ts is None:
        return []
    
    # El modelo ganador (que es un pipeline) ya incluye el scaler, ¡solo lo usamos!
    predicciones = modelo_ts.predict(df_futuro[TS_FEATURES])
    
    return predicciones

def clasificar_cliente(kmeans_model, scaler_rfm, recency, frequency, monetary):
    """
    Clasifica un cliente nuevo/existente en un cluster RFM.
    """
    if kmeans_model is None:
        return "Error de carga"

    # Crear el input
    data_in = pd.DataFrame([[recency, frequency, monetary]], 
                           columns=['Recency', 'Frequency', 'Monetary'])
    
    # Escalar (usando el scaler guardado)
    scaled_data = scaler_rfm.transform(data_in)
    
    # Predecir el cluster
    cluster = kmeans_model.predict(scaled_data)[0]
    
    return cluster