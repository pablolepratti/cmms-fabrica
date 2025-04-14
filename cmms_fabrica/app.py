import streamlit as st
import httpagentparser
from streamlit.web.server.websocket_headers import _get_websocket_headers

# -----------------------------
# 🔍 Detección de dispositivo
# -----------------------------
def detectar_dispositivo():
    try:
        ua = _get_websocket_headers().get("User-Agent", "")
        info = httpagentparser.detect(ua)
        if "platform" in info and "name" in info["platform"]:
            plataforma = info["platform"]["name"]
        else:
            plataforma = "Desconocido"
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
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

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
        st.warning("Esta sección no está disponible en versión móvil.")
    else:
        st.header(f"📱 {modo}")
        st.info("Este módulo se mostrará pronto en versión móvil.")
else:
    # -----------------------------
    # 🧱 Navegación principal
    # -----------------------------
    if modo == "Inicio":
        st.title("📊 Dashboard CMMS")
        st.info("Acá irá el resumen general con KPIs.")
    elif modo == "Máquinas":
        st.title("🏭 Gestión de Máquinas y Sistemas")
        st.info("Módulo de máquinas en desarrollo.")
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
