import streamlit as st
import pandas as pd
import os

CSV_PATH = "data/mantenimientos_preventivos.csv"

def cargar_mantenimientos():
    columnas = [
        "id_mantenimiento", "activo", "sector", "tipo_activo",
        "frecuencia", "modo", "tiempo_estimado", "planilla_asociada",
        "ultimo_mantenimiento", "proximo_mantenimiento", "estado", "responsable"
    ]
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def mostrar_mantenimiento():
    st.subheader("🗓️ Calendario Preventivo Mensual")
    df = cargar_mantenimientos()

    if df.empty:
        st.info("No hay planes de mantenimiento cargados.")
        return

    # Filtros estratégicos
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_sector = st.selectbox("Filtrar por sector", ["Todos"] + sorted(df["sector"].dropna().unique()))
    with col2:
        filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "pendiente", "realizado", "no realizado"])
    with col3:
        filtro_frecuencia = st.selectbox("Filtrar por frecuencia", ["Todas"] + sorted(df["frecuencia"].dropna().unique()))

    if filtro_sector != "Todos":
        df = df[df["sector"] == filtro_sector]
    if filtro_estado != "Todos":
        df = df[df["estado"] == filtro_estado]
    if filtro_frecuencia != "Todas":
        df = df[df["frecuencia"] == filtro_frecuencia]

    st.dataframe(df.sort_values("proximo_mantenimiento"), use_container_width=True)

def app_mantenimiento():
    mostrar_mantenimiento()
