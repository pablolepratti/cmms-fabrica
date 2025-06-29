import streamlit as st
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

# 🔐 Login y cierre de sesión
from cmms_fabrica.modulos.app_login import login_usuario, cerrar_sesion
from cmms_fabrica.modulos.conexion_mongo import db

# 💄 Estilos responsive
from cmms_fabrica.modulos.estilos import aplicar_estilos


# Nuevos módulos CRUD centrados en activos técnicos
from cmms_fabrica.crud.crud_activos_tecnicos import app as crud_activos_tecnicos
from cmms_fabrica.crud.crud_planes_preventivos import app as crud_planes_preventivos
from cmms_fabrica.crud.crud_tareas_correctivas import app as crud_tareas_correctivas
from cmms_fabrica.crud.crud_tareas_tecnicas import app as crud_tareas_tecnicas
from cmms_fabrica.crud.crud_observaciones import app as crud_observaciones
from cmms_fabrica.crud.crud_calibraciones_instrumentos import app as crud_calibraciones
from cmms_fabrica.crud.crud_servicios_externos import app as crud_servicios
from cmms_fabrica.crud.dashboard_kpi_historial import app as kpi_historial
from cmms_fabrica.crud.crud_inventario import app_inventario

# Módulo de usuarios (admin)
from cmms_fabrica.modulos.app_usuarios import app_usuarios

# Gestión de IDs manuales
from cmms_fabrica.modulos.cambiar_ids import app as cambiar_ids

# Reportes técnicos
from cmms_fabrica.modulos.app_reportes import app as app_reportes

# 📱 Estilos responsive
aplicar_estilos()

# 🔐 Login de usuario
usuario, rol = login_usuario()
if not usuario:
    st.stop()

# 🚪 Botón de cerrar sesión
with st.sidebar:
    st.divider()
    st.markdown(f"👤 **{usuario}** ({rol})")
    st.button("Cerrar sesión", on_click=cerrar_sesion, use_container_width=True)

# 📋 Menú lateral (CMMS nuevo completo)
menu = [
    "🏠 Inicio",
    "🧱 Activos Técnicos",
    "📑 Planes Preventivos",
    "🚨 Tareas Correctivas",
    "📂 Tareas Técnicas",
    "🔍 Observaciones Técnicas",
    "📦 Inventario Técnico",
    "🧪 Calibraciones",
    "🏢 Servicios Técnicos",
    "📊 KPIs Globales",
    "📄 Reportes Técnicos",
    "🆔 Cambiar IDs manuales" if rol == "admin" else None,
    "👥 Usuarios" if rol == "admin" else None,
]
menu = [m for m in menu if m is not None]

opcion = st.sidebar.radio("Menú principal", menu)

# 🧭 Enrutamiento
if opcion == "🏠 Inicio":
    st.title("Bienvenido al CMMS de la Fábrica")
    kpi_historial()

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

elif opcion == "📦 Inventario Técnico":
    app_inventario(usuario)

elif opcion == "🧪 Calibraciones":
    crud_calibraciones()

elif opcion == "🏢 Servicios Técnicos":
    crud_servicios()

elif opcion == "📊 KPIs Globales":
    kpi_historial()

elif opcion == "📄 Reportes Técnicos":
    app_reportes()

elif opcion == "🆔 Cambiar IDs manuales":
    cambiar_ids()

elif opcion == "👥 Usuarios" and rol == "admin":
    app_usuarios(usuario, rol)
