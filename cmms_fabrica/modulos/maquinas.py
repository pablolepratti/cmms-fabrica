import streamlit as st
import pandas as pd
import os

DATA_PATH = "data/maquinas.csv"

def cargar_datos():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=["id", "nombre", "tipo_activo", "sector", "estado", "mantenimiento_responsable", "observaciones"])

def mostrar_maquinas():
    st.subheader("📋 Listado de Máquinas y Sistemas")
    df = cargar_datos()

    if df.empty:
        st.warning("No hay máquinas ni sistemas registrados.")
    else:
        st.dataframe(df, use_container_width=True)

        sectores = df["sector"].unique().tolist()
        filtro_sector = st.selectbox("Filtrar por sector", ["Todos"] + sectores)
        if filtro_sector != "Todos":
            df = df[df["sector"] == filtro_sector]
            st.dataframe(df, use_container_width=True)

def app_maquinas():
    mostrar_maquinas()
