import streamlit as st
import pandas as pd
import os

RUTAS = {
    "Tareas": "data/tareas.csv",
    "Observaciones": "data/observaciones.csv",
    "Servicios": "data/servicios.csv",
    "Historial": "data/historial.csv"
}

def mostrar_reportes():
    st.subheader("🖨️ Reportes Internos")

    opcion = st.selectbox("Seleccionar fuente de datos", list(RUTAS.keys()))
    ruta = RUTAS[opcion]

    if not os.path.exists(ruta):
        st.warning("No hay datos para mostrar en esta sección.")
        return

    df = pd.read_csv(ruta)

    if df.empty:
        st.info("No hay registros para mostrar.")
    else:
        st.write(f"Mostrando los últimos {min(20, len(df))} registros:")
        st.dataframe(df.tail(20), use_container_width=True)

def app_reportes():
    mostrar_reportes()
