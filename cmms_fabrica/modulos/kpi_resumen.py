
import streamlit as st
import pandas as pd
import os

def cargar_csv(ruta):
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    else:
        return pd.DataFrame()

def kpi_resumen_inicio():
    st.markdown("### 🔍 Resumen Rápido de Mantenimiento")

    df_tareas = cargar_csv("data/tareas.csv")
    df_servicios = cargar_csv("data/servicios.csv")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Tareas Internas**")
        st.metric("Pendientes", len(df_tareas[df_tareas["estado"] == "pendiente"]))
        st.metric("Cumplidas", len(df_tareas[df_tareas["estado"] == "cumplida"]))

    with col2:
        st.markdown("**Servicios Externos**")
        st.metric("Vencidos", len(df_servicios[df_servicios["estado"] == "vencido"]))
        st.metric("Realizados", len(df_servicios[df_servicios["estado"] == "realizado"]))
