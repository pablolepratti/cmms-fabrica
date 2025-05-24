
import streamlit as st
from modulos import app_activos, app_mantenimiento, app_tareas, app_tareas_tecnicas, app_calibracion, app_observaciones, app_reportes

st.set_page_config(page_title="CMMS Fábrica", layout="wide")
st.title("🧠 CMMS Fábrica – Sistema de Mantenimiento Preventivo Centrado en el Activo Técnico")

menu = st.sidebar.radio("📂 Seleccioná un módulo", [
    "📋 Activos Técnicos",
    "🔧 Mantenimiento Preventivo",
    "🛠️ Tareas Correctivas",
    "🧪 Tareas Técnicas",
    "🎯 Calibraciones",
    "👁 Observaciones",
    "📊 Reportes"
])

if menu == "📋 Activos Técnicos":
    app_activos.run()
elif menu == "🔧 Mantenimiento Preventivo":
    app_mantenimiento.run()
elif menu == "🛠️ Tareas Correctivas":
    app_tareas.run()
elif menu == "🧪 Tareas Técnicas":
    app_tareas_tecnicas.run()
elif menu == "🎯 Calibraciones":
    app_calibracion.run()
elif menu == "👁 Observaciones":
    app_observaciones.run()
elif menu == "📊 Reportes":
    app_reportes.run()
