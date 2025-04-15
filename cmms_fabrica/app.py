
import streamlit as st
from modulos.app_inventario import app_inventario
from modulos.app_maquinas import app_maquinas
from modulos.app_observaciones import app_observaciones
from modulos.app_tareas import app_tareas
from modulos.app_servicios_ext import app_servicios_ext
from modulos.app_reportes import app_reportes
from modulos.app_kpi import app_kpi
from modulos.app_mantenimiento import app_mantenimiento
from modulos.app_semana import app_semana
from modulos.app_usuarios import app_usuarios
from modulos.kpi_resumen import kpi_resumen_inicio

# Título principal
st.set_page_config(page_title="CMMS Fábrica", layout="wide")
#st.sidebar.image("https://img.icons8.com/fluency/48/maintenance.png", use_column_width=True)
st.sidebar.title("🔧 CMMS Fábrica")
seccion = st.sidebar.radio("Seleccionar módulo:", [
    "Inicio", "Máquinas", "Tareas", "Observaciones", "Inventario",
    "Servicios Externos", "Reportes", "KPIs", "Mantenimiento", "Semana"
])

if seccion == "Inicio":
    st.title("📊 Dashboard CMMS")
    st.info("Resumen rápido con indicadores clave.")
    kpi_resumen_inicio()

elif seccion == "Inventario":
    app_inventario()

elif seccion == "Máquinas":
    app_maquinas()

elif seccion == "Tareas":
    app_tareas()

elif seccion == "Observaciones":
    app_observaciones()

elif seccion == "Servicios Externos":
    app_servicios_ext()

elif seccion == "Reportes":
    app_reportes()

elif seccion == "KPIs":
    app_kpi()

elif seccion == "Mantenimiento":
    app_mantenimiento()

elif seccion == "Semana":
    app_semana()

# Módulo solo visible para administrador
if "usuario" in st.session_state and st.session_state["usuario"] == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Opciones Avanzadas")
    if st.sidebar.checkbox("🧑‍💼 Gestión de Usuarios"):
        app_usuarios()
