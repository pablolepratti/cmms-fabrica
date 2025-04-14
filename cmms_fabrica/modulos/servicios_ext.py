import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/servicios.csv"

def cargar_servicios():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=["id_servicio", "id_activo", "empresa", "fecha_realizacion", "descripcion", "periodicidad", "proxima_fecha", "estado", "responsable_fabrica", "observaciones"])

def mostrar_servicios():
    st.subheader("🔧 Servicios Externos")
    df = cargar_servicios()

    if df.empty:
        st.warning("No hay servicios registrados.")
        return

    filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "pendiente", "realizado", "vencido"])
    if filtro_estado != "Todos":
        df = df[df["estado"] == filtro_estado]

    filtro_empresa = st.selectbox("Filtrar por empresa", ["Todas"] + sorted(df["empresa"].dropna().unique()))
    if filtro_empresa != "Todas":
        df = df[df["empresa"] == filtro_empresa]

    st.dataframe(df.sort_values("proxima_fecha", ascending=True), use_container_width=True)

def app_servicios_ext():
    mostrar_servicios()
