import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modulos.conexion_mongo import db

coleccion = db["calibracion_instrumentos"]


def app_calibracion():
    st.subheader("📏 Calibración de Instrumentos de Laboratorio")

    # Cargar datos de MongoDB
    datos = list(coleccion.find({}, {"_id": 0}))
    df = pd.DataFrame(datos)

    if df.empty:
        st.info("No hay instrumentos registrados.")
        return

    # Convertir fecha_proxima si existe
    if "fecha_proxima" in df.columns:
        df["fecha_proxima"] = pd.to_datetime(df["fecha_proxima"], errors='coerce')

    # Filtros
    st.markdown("### ⚠️ Instrumentos con calibración vencida o próxima")
    hoy = datetime.today()
    df_alerta = df[df["fecha_proxima"].notna() & (df["fecha_proxima"] <= hoy + timedelta(days=30))]

    if not df_alerta.empty:
        st.dataframe(df_alerta[["id_instrumento", "nombre", "fecha_proxima", "frecuencia_calibracion"]])
    else:
        st.success("Todos los instrumentos están al día ✅")

    st.markdown("### 🔍 Ver todos los instrumentos")
    filtro_tipo = st.selectbox("Filtrar por tipo de control", ["Todos"] + sorted(df["tipo_control"].dropna().unique().tolist()))

    if filtro_tipo != "Todos":
        df = df[df["tipo_control"] == filtro_tipo]

    st.dataframe(df[["id_instrumento", "nombre", "tipo_control", "frecuencia_calibracion", "fecha_proxima"]])

    st.markdown("### 🔍 Ver detalles de un instrumento")
    seleccion = st.selectbox("Seleccioná un instrumento", df["id_instrumento"])

    if seleccion:
        doc = df[df["id_instrumento"] == seleccion].iloc[0].to_dict()
        for k, v in doc.items():
            st.write(f"**{k.replace('_', ' ').capitalize()}:** {v}")

        st.markdown("Este instrumento se apoya en un instructivo interno para su calibración. Consultar documentación técnica o responsable del laboratorio.")
