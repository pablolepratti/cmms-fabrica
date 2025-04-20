import streamlit as st

# 🔐 Login y cierre de sesión
from modulos.app_login import login_usuario, cerrar_sesion
from modulos.conexion_mongo import db

# 🎨 Estilos responsivos
from modulos.estilos import mobile

# 📋 Funciones principales
from modulos.app_maquinas import app_maquinas
from modulos.app_tareas import app_tareas
from modulos.app_mantenimiento import app_mantenimiento
from modulos.app_inventario import app_inventario
from modulos.historial import log_evento
from modulos.app_observaciones import app_observaciones
from modulos.app_usuarios import app_usuarios
from modulos.app_servicios_ext import app_servicios_ext
from modulos.app_semana import app_semana
from modulos.app_reportes import app_reportes
from modulos.app_kpi import kpi_resumen_inicio
from modulos.cambiar_ids_generales import cambiar_ids_generales

# ⚙️ Configuración de la app
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

# 🔐 Login de usuario
usuario = login_usuario()
if not usuario:
    st.stop()

# ✅ Estilos móviles aplicados
mobile()

# 📋 Menú principal
menu = [
    "🏠 Inicio",
    "📋 Máquinas",
    "📅 Tareas",
    "🛠️ Mantenimientos",
    "🧾 Inventario",
    "📚 Historial",
    "🛠️ Observaciones",
    "👥 Usuarios",
    "⚙️ Editar usuarios",
    "🔧 Servicios externos",
    "📆 Semana",
    "📈 Reportes",
    "📊 Indicadores",
    "✏️ Cambiar IDs manuales",
    "🚪 Cerrar sesión"
]

seleccion = st.sidebar.selectbox("Menú principal", menu)

# 🚦 Navegación
if seleccion == "🏠 Inicio":
    st.title("Bienvenido al CMMS de la Fábrica")
    kpi_resumen_inicio()

elif seleccion == "📋 Máquinas":
    app_maquinas()

elif seleccion == "📅 Tareas":
    app_tareas()

elif seleccion == "🛠️ Mantenimientos":
    app_mantenimientos()

elif seleccion == "🧾 Inventario":
    app_inventario()

elif seleccion == "📚 Historial":
    app_historial()

elif seleccion == "🛠️ Observaciones":
    app_observaciones()

elif seleccion == "👥 Usuarios":
    app_usuarios(usuario.get("usuario"), usuario.get("rol"))

elif seleccion == "⚙️ Editar usuarios":
    if usuario.get("rol") == "admin":
        app_usuarios(usuario.get("usuario"), usuario.get("rol"))
    else:
        st.error("🚫 Acceso denegado. Solo administradores pueden editar usuarios.")

elif seleccion == "🔧 Servicios externos":
    app_servicios_ext()

elif seleccion == "📆 Semana":
    app_semana()

elif seleccion == "📈 Reportes":
    app_reportes()

elif seleccion == "📊 Indicadores":
    st.info("📊 Este módulo se encuentra en desarrollo.")

elif seleccion == "✏️ Cambiar IDs manuales":
    cambiar_ids_generales()

elif seleccion == "🚪 Cerrar sesión":
    cerrar_sesion()
    st.success("👋 Sesión cerrada correctamente. Recargá la app para volver a iniciar.")
    st.stop()
