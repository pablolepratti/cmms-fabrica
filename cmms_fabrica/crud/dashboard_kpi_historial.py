import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["historial"]

def app():

st.title("📊 Dashboard de KPIs – Historial Técnico")

# Filtros
st.sidebar.header("📅 Filtros")
fecha_inicio = st.sidebar.date_input("Desde", value=datetime(2024, 1, 1))
fecha_fin = st.sidebar.date_input("Hasta", value=datetime.today())
tipo_evento = st.sidebar.multiselect("Tipo de Evento", ["preventiva", "correctiva", "tecnica", "observacion", "calibracion"], default=["preventiva", "correctiva"])

# Consulta
query = {
    "fecha_evento": {"$gte": datetime.combine(fecha_inicio, datetime.min.time()),
                     "$lte": datetime.combine(fecha_fin, datetime.max.time())},
    "tipo_evento": {"$in": tipo_evento}
}
registros = list(coleccion.find(query))
df = pd.DataFrame(registros)

if df.empty:
    st.warning("No hay datos en el período seleccionado.")
    st.stop()

# Conversión de fecha
df["fecha_evento"] = pd.to_datetime(df["fecha_evento"])
df["mes"] = df["fecha_evento"].dt.to_period("M")

# KPIs Principales
st.header("📌 Indicadores Clave")
col1, col2, col3 = st.columns(3)

col1.metric("Eventos Registrados", len(df))
col2.metric("Activos Afectados", df["id_activo_tecnico"].nunique())
col3.metric("Usuarios Participantes", df["usuario_registro"].nunique())

# Gráfico: Eventos por tipo
st.subheader("📈 Eventos por Tipo")
tipo_counts = df["tipo_evento"].value_counts()
fig1, ax1 = plt.subplots()
tipo_counts.plot(kind="bar", ax=ax1)
ax1.set_ylabel("Cantidad")
ax1.set_xlabel("Tipo de Evento")
ax1.set_title("Eventos registrados por tipo")
st.pyplot(fig1)

# Gráfico: Evolución mensual
st.subheader("📆 Evolución Mensual de Eventos")
mensual = df.groupby(["mes", "tipo_evento"]).size().unstack(fill_value=0)
fig2, ax2 = plt.subplots()
mensual.plot(ax=ax2)
ax2.set_ylabel("Cantidad")
ax2.set_title("Evolución mensual por tipo de evento")
st.pyplot(fig2)

# Tabla detallada
st.subheader("📋 Detalle de Eventos")
st.dataframe(df[["fecha_evento", "tipo_evento", "id_activo_tecnico", "descripcion", "usuario_registro"]].sort_values("fecha_evento", ascending=False))

if __name__ == "__main__":
    app()
