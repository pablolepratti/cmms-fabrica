from datetime import datetime
import streamlit as st
import pandas as pd
from modulos.conexion_mongo import db

coleccion_historial = db["historial"]

# 🧾 Función para registrar eventos
def log_evento(usuario, evento, id_referencia, tipo_origen, detalle):
    if not usuario or not evento:
        print("[ADVERTENCIA] Registro omitido por falta de usuario o evento.")
        return

    fila = {
        "fecha": datetime.now().isoformat(),
        "usuario": usuario,
        "evento": evento,
        "id_referencia": id_referencia,
        "tipo_origen": tipo_origen,
        "detalle": detalle
    }

    try:
        coleccion_historial.insert_one(fila)
    except Exception as e:
        print(f"[ERROR] No se pudo registrar en historial (Mongo): {e}")


# 📋 Función para mostrar historial en la app
def app_historial():
    st.subheader("📜 Historial de Eventos")

    # Obtener los datos desde MongoDB
    datos = list(coleccion_historial.find({}, {"_id": 0}))
    if not datos:
        st.info("No hay registros en el historial.")
        return

    df = pd.DataFrame(datos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha", ascending=False)

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        usuario = st.selectbox("Filtrar por usuario", ["Todos"] + sorted(df["usuario"].dropna().unique().tolist()))
    with col2:
        evento = st.selectbox("Filtrar por evento", ["Todos"] + sorted(df["evento"].dropna().unique().tolist()))
    with col3:
        tipo = st.selectbox("Filtrar por origen", ["Todos"] + sorted(df["tipo_origen"].dropna().unique().tolist()))

    if usuario != "Todos":
        df = df[df["usuario"] == usuario]
    if evento != "Todos":
        df = df[df["evento"] == evento]
    if tipo != "Todos":
        df = df[df["tipo_origen"] == tipo]

    # Mostrar resultados
    st.dataframe(df, use_container_width=True)
