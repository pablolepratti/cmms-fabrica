import streamlit as st
import pandas as pd
import os

def cargar_csv(ruta):
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    else:
        return pd.DataFrame()

def mostrar_kpis():
    st.subheader("📈 Indicadores Clave de Mantenimiento")

    df_tareas = cargar_csv("data/tareas.csv")
    df_servicios = cargar_csv("data/servicios.csv")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧰 Tareas Internas")
        total = len(df_tareas)
        pendientes = len(df_tareas[df_tareas["estado"] == "pendiente"])
        cumplidas = len(df_tareas[df_tareas["estado"] == "cumplida"])
        st.metric("Total", total)
        st.metric("Pendientes", pendientes)
        st.metric("Cumplidas", cumplidas)

    with col2:
        st.markdown("### 🛠️ Servicios Externos")
        total_s = len(df_servicios)
        vencidos = len(df_servicios[df_servicios["estado"] == "vencido"])
        realizados = len(df_servicios[df_servicios["estado"] == "realizado"])
        st.metric("Total", total_s)
        st.metric("Realizados", realizados)
        st.metric("Vencidos", vencidos)

def app_kpi():
    mostrar_kpis()
