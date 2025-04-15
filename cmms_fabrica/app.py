import streamlit as st
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

import httpagentparser

# Importar funciones principales de cada módulo
from modulos.maquinas import app_maquinas
from modulos.tareas import app_tareas
from modulos.observaciones import app_observaciones
from modulos.inventario import app_inventario
from modulos.servicios_ext import app_servicios_ext
from modulos.reportes import app_reportes
from modulos.kpi import app_kpi
from modulos.mantenimiento import app_mantenimiento

# -----------------------------
# 🔍 Detección de dispositivo
# -----------------------------
def detectar_dispositivo():
    try:
        ctx = st.runtime.scriptrunner.get_script_run_context()
        ua = ctx.request.headers.get("User-Agent", "")
        info = httpagentparser.detect(ua)
        if "Mobile" in str(info):
            return "mobile"
        else:
            return "desktop"
    except:
        return "desktop"

dispositivo = detectar_dispositivo()

# -----------------------------
# 🎨 Layout general
# -----------------------------
st.sidebar.title("🛠️ CMMS Fábrica")
modo = st.sidebar.radio("Seleccionar módulo:", (
    "Inicio", "Mantenimiento", "Máquinas", "Tareas", "Observaciones",
    "Inventario", "Servicios Externos", "Reportes", "KPIs"
))

# -----------------------------
# 👁️ Versión simplificada mobile
# -----------------------------
if dispositivo == "mobile":
    st.sidebar.markdown("📱 *Versión simplificada móvil*")
    if modo not in ["Tareas", "Observaciones", "Inventario"]:
        st.warning("Esta sección no está disponible en versión móvil.")
    else:
        st.header(f"📱 {modo}")
        if modo == "Tareas":
            app_tareas()
        elif modo == "Observaciones":
            app_observaciones()
        elif modo == "Inventario":
            app_inventario()
else:
    # -----------------------------
    # 🧱 Navegación principal
    # -----------------------------
    if modo == "Inicio":
        st.title("📊 Dashboard CMMS")
        st.info("Bienvenido al sistema. Seleccioná un módulo del menú.")
    elif modo == "Mantenimiento":
        app_mantenimiento()
    elif modo == "Máquinas":
        app_maquinas()
    elif modo == "Tareas":
        app_tareas()
    elif modo == "Observaciones":
        app_observaciones()
    elif modo == "Inventario":
        app_inventario()
    elif modo == "Servicios Externos":
        app_servicios_ext()
    elif modo == "Reportes":
        app_reportes()
    elif modo == "KPIs":
        app_kpi()
