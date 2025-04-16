import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/observaciones.csv"
TAREAS_PATH = "data/tareas.csv"

def cargar_observaciones():
    columnas = [
        "id_obs", "id_maquina", "fecha", "descripcion", "autor",
        "criticidad", "crear_tarea", "estado", "tarea_relacionada"
    ]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_observaciones(df):
    df.to_csv(DATA_PATH, index=False)

def crear_tarea_automatica(id_obs, id_maquina, descripcion):
    if os.path.exists(TAREAS_PATH):
        df_tareas = pd.read_csv(TAREAS_PATH)
    else:
        df_tareas = pd.DataFrame(columns=[
            "id_tarea", "id_maquina", "descripcion", "tipo_tarea", "origen",
            "ultima_ejecucion", "proxima_ejecucion", "estado", "observaciones"
        ])
    
    nuevo_id_tarea = f"TAR{len(df_tareas)+1:04d}"
    hoy = datetime.today().strftime("%Y-%m-%d")

    nueva_tarea = {
        "id_tarea": nuevo_id_tarea,
        "id_maquina": id_maquina,
        "descripcion": f"[Desde observación {id_obs}] {descripcion}",
        "tipo_tarea": "correctiva",
        "origen": "observacion",
        "ultima_ejecucion": hoy,
        "proxima_ejecucion": hoy,
        "estado": "pendiente",
        "observaciones": f"Generada automáticamente desde observación {id_obs}"
    }

    df_tareas = pd.concat([df_tareas, pd.DataFrame([nueva_tarea])], ignore_index=True)
    df_tareas.to_csv(TAREAS_PATH, index=False)
    st.success(f"🛠️ Tarea {nuevo_id_tarea} creada automáticamente desde la observación.")

def app_observ_
