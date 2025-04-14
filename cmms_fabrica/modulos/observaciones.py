import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/observaciones.csv"

def cargar_observaciones():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=["id_obs", "id_maquina", "fecha", "descripcion", "autor", "criticidad", "crear_tarea", "estado", "tarea_relacionada"])

def guardar_observaciones(df):
    df.to_csv(DATA_PATH, index=False)

def mostrar_observaciones():
    st.subheader("📋 Observaciones Técnicas")
    df = cargar_observaciones()

    if df.empty:
        st.warning("No hay observaciones registradas.")
        return

    # Filtro por criticidad
    crit = st.selectbox("Filtrar por criticidad", ["Todas", "baja", "media", "alta"])
    if crit != "Todas":
        df = df[df["criticidad"] == crit]

    st.dataframe(df.sort_values("fecha", ascending=False), use_container_width=True)

def app_observaciones():
    mostrar_observaciones()
