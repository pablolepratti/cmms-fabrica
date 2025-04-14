import os
import pandas as pd
from datetime import datetime
from modulos.historial import log_evento

CARPETA_DATA = "data"
LIMITE_MB = 400

# Archivos CSV a gestionar
csv_rotables = {
    "historial.csv": "fecha",
    "observaciones.csv": "fecha",
    "tareas.csv": "ultima_ejecucion",
    "servicios.csv": "fecha_realizacion"
}

def obtener_tamano_total_mb():
    total_bytes = 0
    for archivo in os.listdir(CARPETA_DATA):
        path = os.path.join(CARPETA_DATA, archivo)
        if os.path.isfile(path):
            total_bytes += os.path.getsize(path)
    return total_bytes / (1024 * 1024)

def limpiar_csv_por_fecha(nombre_archivo, campo_fecha, max_filas=None):
    ruta = os.path.join(CARPETA_DATA, nombre_archivo)
    try:
        df = pd.read_csv(ruta)
        if campo_fecha not in df.columns or len(df) < 100:
            return 0
        df[campo_fecha] = pd.to_datetime(df[campo_fecha], errors='coerce')
        df = df.sort_values(by=campo_fecha)
        filas_a_borrar = int(len(df) * 0.3) if max_filas is None else max_filas
        df = df.iloc[filas_a_borrar:]
        df.to_csv(ruta, index=False)
        return filas_a_borrar
    except:
        return 0

def ejecutar_limpieza_si_es_necesario():
    uso_actual = obtener_tamano_total_mb()
    if uso_actual < LIMITE_MB:
        return False

    archivos_ordenados = sorted(
        csv_rotables.items(),
        key=lambda x: os.path.getsize(os.path.join(CARPETA_DATA, x[0])),
        reverse=True
    )

    total_filas_eliminadas = 0
    for nombre_archivo, campo_fecha in archivos_ordenados:
        filas = limpiar_csv_por_fecha(nombre_archivo, campo_fecha)
        if filas > 0:
            log_evento("sistema", "Limpieza automática de almacenamiento", nombre_archivo, "almacenamiento", f"Se eliminaron {filas} filas por exceso de espacio.")
            total_filas_eliminadas += filas
        if obtener_tamano_total_mb() < LIMITE_MB:
            break

    return total_filas_eliminadas > 0
