import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/tareas.csv"

def cargar_tareas():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=["id_tarea", "id_maquina", "descripcion", "tipo_tarea", "origen", "ultima_ejecucion", "proxima_ejecucion", "estado", "observaciones"])

def guardar_tareas(df):
    df.to_csv(DATA_PATH, index=False)

def mostrar_tareas():
    st.subheader("📅 Tareas de Mantenimiento")
    df = cargar_tareas()

    if df.empty:
        st.warning("No hay tareas registradas.")
        return

    # Filtro por estado
    estado = st.selectbox("Filtrar por estado", ["Todos", "pendiente", "realizada"])
    if estado != "Todos":
        df = df[df["estado"] == estado]

    # Filtro por tipo
    tipo = st.selectbox("Filtrar por tipo de tarea", ["Todas", "mantenimiento", "inspección"])
    if tipo != "Todas":
        df = df[df["tipo_tarea"] == tipo]

    st.dataframe(df.sort_values("proxima_ejecucion"), use_container_width=True)

def app_tareas():
    mostrar_tareas()
