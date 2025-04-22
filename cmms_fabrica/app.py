import streamlit as st
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

# 🔐 Login y cierre de sesión
from modulos.app_login import login_usuario, cerrar_sesion
from modulos.conexion_mongo import db

# 💄 Estilos responsive
from modulos.estilos import mobile

# 🧠 Funciones principales
from modulos.app_maquinas import app_maquinas
from modulos.app_tareas import app_tareas
from modulos.app_mantenimiento import app_mantenimiento
from modulos import app_calibracion_instrumentos
from modulos.app_inventario import app_inventario
from modulos.historial import log_evento  # <-- historial = función de logging
from modulos.historial import app_historial
from modulos.app_usuarios import app_usuarios
from modulos.app_semana import app_semana
from modulos.app_observaciones import app_observaciones
from modulos.app_servicios_ext import app_servicios_ext
from modulos.app_reportes import app_reportes
from modulos.app_kpi import app_kpi
from modulos.kpi_resumen import kpi_resumen_inicio
from modulos.cambiar_ids_generales import cambiar_ids_generales

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
    "🛠️ Mantenimientos",
    "📦 Inventario",
    "🧾 Reportes",
    "📖 Historial",
    "🔍 Observaciones",
    "📆 Plan Semanal",
    "🔧 Servicios Externos",
    "👥 Usuarios" if rol == "admin" else None,
    "✏️ Cambiar IDs manuales" if rol == "admin" else None
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

elif opcion == "🛠️ Mantenimientos":
    app_mantenimiento()  # ✅ corregido

elif opcion == "📏 Calibración de Instrumentos":
    app_calibracion_instrumentos.app_calibracion()

elif opcion == "📦 Inventario":
    app_inventario()

elif opcion == "🧾 Reportes":
    app_reportes()

elif menu == "Historial":
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
