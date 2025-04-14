import csv
import os
import pandas as pd
from datetime import datetime

RUTA_CSV = os.path.join("data", "observaciones.csv")

# Cargar observaciones
def cargar_observaciones():
    return pd.read_csv(RUTA_CSV)

# Guardar observaciones
def guardar_observaciones(df):
    df.to_csv(RUTA_CSV, index=False)

# Registrar nueva observación
def registrar_observacion(obs_dict):
    df = cargar_observaciones()
    df = pd.concat([df, pd.DataFrame([obs_dict])], ignore_index=True)
    guardar_observaciones(df)

# Listar observaciones por máquina
def listar_por_maquina(id_maquina):
    df = cargar_observaciones()
    return df[df["id_maquina"] == id_maquina]

# Convertir observación en tarea
def convertir_en_tarea(id_obs, id_tarea_nueva):
    df = cargar_observaciones()
    if id_obs in df["id_obs"].values:
        df.loc[df["id_obs"] == id_obs, "crear_tarea"] = "sí"
        df.loc[df["id_obs"] == id_obs, "estado"] = "convertida"
        df.loc[df["id_obs"] == id_obs, "tarea_relacionada"] = id_tarea_nueva
        guardar_observaciones(df)
        return True
    return False

# Cerrar una observación sin crear tarea
def cerrar_observacion(id_obs):
    df = cargar_observaciones()
    if id_obs in df["id_obs"].values:
        df.loc[df["id_obs"] == id_obs, "estado"] = "cerrada"
        guardar_observaciones(df)
        return True
    return False

# Ver observaciones pendientes
def listar_pendientes():
    df = cargar_observaciones()
    return df[df["estado"] == "pendiente"]
