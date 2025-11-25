# src/data_processing.py

import pandas as pd
import numpy as np
import re
import glob
import os

# --- CONFIGURACIÓN DE ÍNDICES ---
# AJUSTAR SEGÚN TU EXCEL
IDX_JERARQUIA = 0   
IDX_FECHA = 4       
IDX_CANTIDAD = 8    # Columna I
IDX_MONTO = 10      # Columna K

def load_raw_data(raw_data_path):
    """Carga archivos ignorando el encabezado para leer todo como texto puro."""
    archivos = glob.glob(os.path.join(raw_data_path, "*.xlsx")) + glob.glob(os.path.join(raw_data_path, "*.csv"))
    print(f"📂 Encontrados {len(archivos)} archivos.")
    
    dfs = []
    for archivo in archivos:
        try:
            if archivo.endswith('.xlsx'):
                # dtype=str es vital para que no interprete números automáticamente
                df = pd.read_excel(archivo, dtype=str, header=None)
            else:
                df = pd.read_csv(archivo, dtype=str, low_memory=False, header=None, on_bad_lines='skip')
            dfs.append(df)
        except Exception as e:
            print(f"   ⚠️ Error leyendo {archivo}: {e}")
            
    if not dfs: raise ValueError("No hay datos.")
    return pd.concat(dfs, ignore_index=True)

def clean_number_us_format(val):
    """
    CORRECCIÓN: Formato Americano (US)
    - Elimina comas (separador de miles).
    - Mantiene puntos (decimales).
    Ejemplo: "1,200.50" -> 1200.50
    Ejemplo: "1.00" -> 1.0
    """
    if pd.isna(val): return 0.0
    # Limpiar símbolos de moneda y espacios
    s = str(val).replace('Gs', '').replace('$', '').replace('USD', '').strip()
    
    if s == '' or s.lower() == 'nan': return 0.0
    
    # 1. Eliminar comas (son separadores de mil en este formato)
    s = s.replace(',', '')
    
    # 2. El punto ya es decimal en Python, no lo tocamos.
    try:
        return float(s)
    except:
        return 0.0

def clasificar_cliente(nombre):
    if pd.isna(nombre): return 'Particular'
    nombre = nombre.upper()
    if 'OCASIONAL' in nombre: return 'B2C_Ocasional'
    keywords_b2b = ['S.A.', 'S.R.L.', 'LTDA', 'CONSTRUCTORA', 'INGENIERIA', 'CONSORCIO', 'OBRAS']
    if any(k in nombre for k in keywords_b2b):
        return 'B2B_Empresa'
    return 'B2C_Particular'

def process_single_file(filepath):
    """Procesa un archivo con la lógica corregida."""
    print(f"   Processing: {os.path.basename(filepath)}...")
    
    # Cargar
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath, dtype=str, header=None)
    else:
        df = pd.read_csv(filepath, dtype=str, low_memory=False, header=None, on_bad_lines='skip')

    clean_rows = []
    
    cur_client = "Desconocido"
    cur_group = "Sin Grupo"
    cur_product = "Sin Producto"
    
    data_values = df.values
    
    for row in data_values:
        if len(row) <= IDX_MONTO: continue
        col_text = str(row[IDX_JERARQUIA]).strip()
        
        # 1. Detección de Grupo / Cliente / Producto
        if col_text.isupper() and "DOCUMENTO" not in col_text and len(col_text) > 4:
            if re.match(r'^\d+', col_text): # Producto (ej: 5939...)
                cur_product = col_text
                continue
            
            if "S.A." in col_text or "OCASIONAL" in col_text or "," in col_text:
                cur_client = col_text
                cur_group = "Sin Grupo"
            else:
                cur_group = col_text
            continue

        if re.match(r'^\d{2,}', col_text): # Producto (backup)
            cur_product = col_text
            continue

        # 2. Detección de Venta
        if "Documento" in col_text or "Fact." in col_text:
            try:
                # USAMOS LA NUEVA FUNCIÓN CORREGIDA AQUÍ
                monto = clean_number_us_format(row[IDX_MONTO])
                cantidad = clean_number_us_format(row[IDX_CANTIDAD])
                fecha_raw = row[IDX_FECHA]
                
                if monto > 0:
                    clean_rows.append({
                        'Fecha': fecha_raw,
                        'Cliente': cur_client,
                        'Segmento': clasificar_cliente(cur_client),
                        'Grupo': cur_group,
                        'Producto': cur_product,
                        'Cantidad': cantidad,
                        'Total': monto,
                        'Archivo_Origen': os.path.basename(filepath)
                    })
            except Exception:
                continue 

    return pd.DataFrame(clean_rows)

def load_and_process_all(raw_data_path):
    archivos = glob.glob(os.path.join(raw_data_path, "*.csv")) + glob.glob(os.path.join(raw_data_path, "*.xlsx"))
    print(f"📂 Procesando {len(archivos)} archivos...")
    
    all_clean_dfs = []
    for archivo in archivos:
        df_clean = process_single_file(archivo)
        if not df_clean.empty:
            all_clean_dfs.append(df_clean)
    
    if not all_clean_dfs: raise ValueError("Error: No se extrajeron datos.")
        
    df_final = pd.concat(all_clean_dfs, ignore_index=True)
    
    # Normalización final
    df_final['Fecha'] = pd.to_datetime(df_final['Fecha'], dayfirst=True, errors='coerce')
    df_final = df_final.dropna(subset=['Fecha'])
    df_final['Año'] = df_final['Fecha'].dt.year
    df_final['Mes'] = df_final['Fecha'].dt.month
    
    print(f"✅ ¡ÉXITO! {len(df_final)} filas limpias.")
    return df_final