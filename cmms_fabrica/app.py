import streamlit as st
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

# 🔐 Login y cierre de sesión
from modulos.app_login import login_usuario, cerrar_sesion
from modulos.conexion_mongo import db

# 💄 Estilos responsive
from modulos.estilos import mobile

# Módulos del CMMS viejo
from modulos.app_maquinas import app_maquinas
from modulos.app_tareas import app_tareas
from modulos.app_mantenimiento import app_mantenimiento
from modulos.app_calibracion_instruments import app_calibracion
from modulos.app_inventario import app_inventario
from modulos.historial import app_historial
from modulos.app_usuarios import app_usuarios
from modulos.app_semana import app_semana
from modulos.app_observaciones import app_observaciones
from modulos.app_servicios_ext import app_servicios_ext
from modulos.app_reportes import app_reportes
from modulos.kpi_resumen import kpi_resumen_inicio
from modulos.cambiar_ids_generales import cambiar_ids_generales
from modulos.app_tareas_tecnicas import app_tareas_tecnicas

# 🆕 Nuevos módulos CRUD centrados en activos técnicos
from crud.crud_activos_tecnicos import app as crud_activos_tecnicos
from crud.crud_planes_preventivos import app as crud_planes_preventivos
from crud.crud_tareas_correctivas import app as crud_tareas_correctivas
from crud.crud_tareas_tecnicas import app as crud_tareas_tecnicas
from crud.crud_observaciones import app as crud_observaciones
from crud.crud_calibraciones_instrumentos import app as crud_calibraciones
from crud.crud_servicios_externos import app as crud_servicios
from dashboard_kpi_historial import app as kpi_historial

# 📱 Estilos responsive
mobile()

# 🔐 Login de usuario
usuario, rol = login_usuario()
if not usuario:
    st.stop()

# 🚪 Botón de cerrar sesión
with st.sidebar:
    st.divider()
    st.markdown(f"👤 **{usuario}** ({rol})")
    st.button("Cerrar sesión", on_click=cerrar_sesion, use_container_width=True)

# 📋 Menú lateral
menu = [
    "🏠 Inicio",
    "📋 Máquinas",
    "📅 Tareas",
    "📂 Tareas Técnicas Abiertas",
    "🛠️ Mantenimientos",
    "📏 Calibración de Instrumentos",
    "📦 Inventario",
    "🧾 Reportes",
    "📖 Historial",
    "🔍 Observaciones",
    "📆 Plan Semanal",
    "🔧 Servicios Externos",
    "👥 Usuarios" if rol == "admin" else None,
    "✏️ Cambiar IDs manuales" if rol == "admin" else None,
    "--- CMMS NUEVO ---",
    "🧱 Activos Técnicos",
    "📑 Planes Preventivos",
    "🚨 Tareas Correctivas",
    "📂 Tareas Técnicas",
    "🔍 Observaciones Técnicas",
    "🧪 Calibraciones",
    "🏢 Servicios Técnicos",
    "📊 KPIs Globales"
]
menu = [m for m in menu if m is not None]

opcion = st.sidebar.selectbox("Menú principal", menu)

# 🧭 Enrutamiento
if opcion == "🏠 Inicio":
    st.title("Bienvenido al CMMS de la Fábrica")
    kpi_resumen_inicio()

elif opcion == "📋 Máquinas":
    app_maquinas()

elif opcion == "📅 Tareas":
    app_tareas()

elif opcion == "📂 Tareas Técnicas Abiertas":
    app_tareas_tecnicas()

elif opcion == "🛠️ Mantenimientos":
    app_mantenimiento()

elif opcion == "📏 Calibración de Instrumentos":
    app_calibracion()

elif opcion == "📦 Inventario":
    app_inventario()

elif opcion == "🧾 Reportes":
    app_reportes()

elif opcion == "📖 Historial":
    app_historial()

elif opcion == "🔍 Observaciones":
    app_observaciones()

elif opcion == "📆 Plan Semanal":
    app_semana()

elif opcion == "🔧 Servicios Externos":
    app_servicios_ext()

elif opcion == "👥 Usuarios" and rol == "admin":
    app_usuarios(usuario, rol)

elif opcion == "✏️ Cambiar IDs manuales" and rol == "admin":
    cambiar_ids_generales()

# 🔁 Nuevos módulos
elif opcion == "🧱 Activos Técnicos":
    crud_activos_tecnicos()

elif opcion == "📑 Planes Preventivos":
    crud_planes_preventivos()

elif opcion == "🚨 Tareas Correctivas":
    crud_tareas_correctivas()

elif opcion == "📂 Tareas Técnicas":
    crud_tareas_tecnicas()

elif opcion == "🔍 Observaciones Técnicas":
    crud_observaciones()

elif opcion == "🧪 Calibraciones":
    crud_calibraciones()

elif opcion == "🏢 Servicios Técnicos":
    crud_servicios()

elif opcion == "📊 KPIs Globales":
    kpi_historial()
