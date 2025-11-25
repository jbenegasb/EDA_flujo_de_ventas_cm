# src/model_features.py
import pandas as pd
import numpy as np

# --- 1. Funciones para Series Temporales (TS) ---

def crear_lags(df):
    """
    Transforma el dataset de TS (una fila por mes/producto) en un dataset de regresión
    añadiendo las variables de retardo (Lags 1, 2, 3, 12) y el promedio móvil.
    """
    df = df.sort_values(['ID_Producto', 'Fecha_Mensual']).copy()
    
    # Crea los lags por grupo (ID_Producto)
    df['Venta_Mes_Ant'] = df.groupby('ID_Producto')['Cantidad'].shift(1)
    df['Venta_2Meses_Ant'] = df.groupby('ID_Producto')['Cantidad'].shift(2)
    df['Venta_3Meses_Ant'] = df.groupby('ID_Producto')['Cantidad'].shift(3)
    df['Venta_Ano_Ant'] = df.groupby('ID_Producto')['Cantidad'].shift(12)
    
    # Promedio Móvil
    df['Promedio_Movil_3M'] = df[['Venta_Mes_Ant', 'Venta_2Meses_Ant', 'Venta_3Meses_Ant']].mean(axis=1)
    
    return df.dropna()

# --- 2. Funciones para Segmentación de Clientes (RFM) ---

def calcular_rfm(df_completo):
    """
    Calcula las métricas Recency, Frequency y Monetary (RFM) para cada cliente.
    """
    fecha_actual = df_completo['Fecha'].max() + pd.Timedelta(days=1)

    df_clientes = df_completo.groupby('Cliente').agg(
        Recency=('Fecha', lambda x: (fecha_actual - x.max()).days),
        Frequency=('Total', 'count'), 
        Monetary=('Total', 'sum')                          
    ).reset_index()

    return df_clientes[df_clientes['Monetary'] > 0]
