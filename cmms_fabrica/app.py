import streamlit as st
from modulos.maquinas import app_maquinas
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

import httpagentparser

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
    "Inicio", "Máquinas", "Tareas", "Observaciones", "Inventario", "Servicios Externos", "Reportes", "KPIs"
))

# -----------------------------
# 👁️ Versión simplificada mobile
# -----------------------------
if dispositivo == "mobile":
    st.sidebar.markdown("📱 *Versión simplificada móvil*")
    if modo not in ["Tareas", "Observaciones", "Inventario"]:
        st.header(f"📱 {modo}")
        st.info("Este módulo se mostrará pronto en versión móvil.")
    else:
        st.warning("Este módulo aún no está disponible en mobile.")
else:
    # -----------------------------
    # 🧱 Navegación principal
    # -----------------------------
    if modo == "Inicio":
        st.title("📊 Dashboard CMMS")
        st.info("Acá irá el resumen general con KPIs.")
    elif modo == "Máquinas":
        app_maquinas()
    elif modo == "Tareas":
        st.title("🗓️ Gestión de Tareas")
        st.info("Módulo de tareas en desarrollo.")
    elif modo == "Observaciones":
        st.title("📝 Observaciones Técnicas")
        st.info("Módulo de observaciones en desarrollo.")
    elif modo == "Inventario":
        st.title("📦 Inventario Técnico")
        st.info("Módulo de inventario en desarrollo.")
    elif modo == "Servicios Externos":
        st.title("🔧 Servicios Tercerizados")
        st.info("Módulo de servicios externos en desarrollo.")
    elif modo == "Reportes":
        st.title("🖨️ Generación de Reportes")
        st.info("Módulo de reportes en desarrollo.")
    elif modo == "KPIs":
        st.title("📈 Indicadores Clave de Desempeño")
        st.info("Módulo de KPIs en desarrollo.")
