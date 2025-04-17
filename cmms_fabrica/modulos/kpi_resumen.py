import streamlit as st
import pandas as pd
from modulos.conexion_mongo import db

def cargar_coleccion(nombre):
    return pd.DataFrame(list(db[nombre].find({}, {"_id": 0})))

def kpi_resumen_inicio():
    df_tareas = cargar_coleccion("tareas")
    df_servicios = cargar_coleccion("servicios")
    df_mantenimiento = cargar_coleccion("mantenimientos")

    # 🔧 Asegurar columnas 'estado' en string para evitar errores
    for df in [df_tareas, df_servicios, df_mantenimiento]:
        if "estado" in df.columns:
            df["estado"] = df["estado"].astype(str)

    st.markdown("### 📊 Resumen del sistema")

    col_tareas, col_servicios, col_mant = st.columns(3)

    with col_tareas:
        pendientes = len(df_tareas[df_tareas["estado"] == "pendiente"])
        st.metric("🧰 Tareas pendientes", pendientes)

    with col_servicios:
        vencidos = len(df_servicios[df_servicios["estado"] == "vencido"])
        st.metric("🛠️ Servicios vencidos", vencidos)

    with col_mant:
        no_realizados = len(df_mantenimiento[df_mantenimiento["estado"] == "no realizado"])
        st.metric("📅 Mantenimientos no realizados", no_realizados)

