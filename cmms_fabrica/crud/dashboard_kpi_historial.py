"""
📊 Dashboard de KPIs – Historial Técnico – CMMS Fábrica

Este módulo presenta indicadores clave de mantenimiento y soporte técnico a partir de la colección historial,
que consolida eventos preventivos, correctivos, técnicos, observaciones y calibraciones.

✅ Normas aplicables:
- ISO 55001 (Indicadores de gestión de mantenimiento alineados al ciclo de vida del activo)
- ISO 14224 (Clasificación y análisis de eventos técnicos)
- ISO 9001:2015 (Control y seguimiento de procesos mediante indicadores de desempeño)
"""

import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["historial"]
activos_tecnicos = db["activos_tecnicos"]

def app():
    st.title("📊 Dashboard de KPIs – Historial Técnico")
    
    # Filtros
    st.sidebar.header("📅 Filtros")
    fecha_inicio = st.sidebar.date_input("Desde", value=datetime(2025, 1, 1))
    fecha_fin = st.sidebar.date_input("Hasta", value=datetime.today())
    tipo_evento = st.sidebar.multiselect("Tipo de Evento", ["preventiva", "correctiva", "tecnica", "observacion", "calibracion"],
                                         default=["preventiva", "correctiva", "tecnica", "observacion", "calibracion"])

    # Filtro por activo técnico o conjunto
    st.sidebar.header("🧩 Activo Técnico (opcional)")
    activos = list(activos_tecnicos.find())
    opciones = ["Todos"] + sorted([a["id_activo_tecnico"] for a in activos if "id_activo_tecnico" in a])
    id_filtrado = st.sidebar.selectbox("Filtrar por ID de activo técnico (incluye subactivos)", opciones)

    # Construir lista de IDs válidos
    ids_filtrados = None
    if id_filtrado != "Todos":
        subactivos = [a["id_activo_tecnico"] for a in activos if a.get("pertenece_a") == id_filtrado]
        ids_filtrados = [id_filtrado] + subactivos
        st.sidebar.success(f"Incluyendo {len(subactivos)} subactivo(s) de '{id_filtrado}'")

    # Consulta
    query = {
        "fecha_evento": {
            "$gte": datetime.combine(fecha_inicio, datetime.min.time()),
            "$lte": datetime.combine(fecha_fin, datetime.max.time())
        },
        "tipo_evento": {"$in": tipo_evento}
    }

    if ids_filtrados:
        query["id_activo_tecnico"] = {"$in": ids_filtrados}

    registros = list(coleccion.find(query))
    df = pd.DataFrame(registros)

    if df.empty:
        st.warning("No hay datos en el período seleccionado.")
        st.stop()

    # Procesamiento
    df["fecha_evento"] = pd.to_datetime(df["fecha_evento"])
    df["mes"] = df["fecha_evento"].dt.to_period("M")
    df["usuario_registro"] = df.get("usuario_registro", df.get("usuario", "desconocido"))

    # KPIs Principales
    st.header("📌 Indicadores Clave")
    col1, col2, col3 = st.columns(3)
    col1.metric("Eventos Registrados", len(df))
    col2.metric("Activos Afectados", df["id_activo_tecnico"].nunique())
    col3.metric("Usuarios Participantes", df["usuario_registro"].nunique())

    # Gráfico: Eventos por tipo
    st.subheader("📈 Eventos por Tipo")
    tipo_counts = df["tipo_evento"].value_counts().sort_index()
    fig1, ax1 = plt.subplots()
    tipo_counts.plot(kind="bar", ax=ax1, color="skyblue", edgecolor="black")
    ax1.set_ylabel("Cantidad")
    ax1.set_xlabel("Tipo de Evento")
    ax1.set_title("Eventos registrados por tipo")
    st.pyplot(fig1)

    # Gráfico: Evolución mensual
    st.subheader("📆 Evolución Mensual de Eventos")
    mensual = df.groupby(["mes", "tipo_evento"]).size().unstack(fill_value=0)
    mensual.index = mensual.index.to_timestamp()

    fig2, ax2 = plt.subplots()
    mensual.plot(ax=ax2, marker="o")
    ax2.set_ylabel("Cantidad")
    ax2.set_xlabel("Mes")
    ax2.set_title("Evolución mensual por tipo de evento")
    ax2.legend(title="Tipo de Evento", loc="upper left")

    # Limitar a 2025 y mejorar etiquetas
    ax2.set_xlim([pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")])
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax2.tick_params(axis='x', rotation=0)
    st.pyplot(fig2)

    # Tabla detallada
    st.subheader("📋 Detalle de Eventos Técnicos")
    st.dataframe(df[[
        "fecha_evento", "tipo_evento", "id_activo_tecnico",
        "descripcion", "usuario_registro"
    ]].sort_values("fecha_evento", ascending=False))

if __name__ == "__main__":
    app()

