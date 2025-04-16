import streamlit as st
import pandas as pd
from modulos.conexion_mongo import db

def cargar_coleccion(nombre):
    return pd.DataFrame(list(db[nombre].find({}, {"_id": 0})))

def kpi_resumen_inicio():
    df_tareas = cargar_coleccion("tareas")
    df_servicios = cargar_coleccion("servicios")
    df_mantenimiento = cargar_coleccion("mantenimientos")

    st.markdown("### 📊 Resumen del sistema")
    col1, col2, col3 = st.columns(3)
    with col1:
        pendientes = len(df_tareas[df_tareas["estado"] == "pendiente"])
        st.metric("🧰 Tareas pendientes", pendientes)
    with col2:
        vencidos = len(df_servicios[df_servicios["estado"] == "vencido"])
        st.metric("🛠️ Servicios vencidos", vencidos)
    with col3:
        no_realizados = len(df_mantenimiento[df_mantenimiento["estado"] == "no realizado"])
        st.metric("📅 Mantenimientos no realizados", no_realizados)
