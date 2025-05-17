import streamlit as st
from utils.mongo_handler import obtener_tareas_activas, obtener_tareas_tecnicas, obtener_observaciones, contar_kpis
from utils.ui_componentes import mostrar_tabla_tareas, mostrar_tabla_tareas_tecnicas, mostrar_tabla_observaciones

st.set_page_config(page_title="Dashboard Técnico CMMS", layout="wide")
st.title("📊 Dashboard Técnico - CMMS Fábrica")

# KPIs
st.subheader("📈 Indicadores Rápidos")
kpis = contar_kpis()
col1, col2 = st.columns(2)
col1.metric("Tareas Pendientes", kpis.get("pendientes", 0))
col2.metric("Tareas Realizadas Hoy", kpis.get("hechas_hoy", 0))

# Tareas activas
st.subheader("🛠️ Tareas Preventivas y Correctivas")
tareas = obtener_tareas_activas()
mostrar_tabla_tareas(tareas)

# Tareas técnicas
st.subheader("📂 Tareas Técnicas Abiertas")
tareas_tecnicas = obtener_tareas_tecnicas()
mostrar_tabla_tareas_tecnicas(tareas_tecnicas)

# Observaciones
st.subheader("🔍 Observaciones Técnicas")
observaciones = obtener_observaciones()
mostrar_tabla_observaciones(observaciones)
