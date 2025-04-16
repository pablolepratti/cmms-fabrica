import streamlit as st
import pandas as pd
import hashlib
import os

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

st.set_page_config(page_title="CMMS Fábrica", layout="wide")

# ---------------------
# 🔐 Login
# ---------------------
def verificar_login():
    st.sidebar.subheader("🔑 Iniciar sesión")
    usuario = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    # 🧪 Bloque DEBUG opcional para ver hash
    if st.sidebar.checkbox("🧪 Ver hash de esta contraseña"):
        st.sidebar.code(hashlib.sha256(password.encode()).hexdigest(), language="bash")

    if st.sidebar.button("Ingresar"):
        if os.path.exists("data/usuarios.csv"):
            df = pd.read_csv("data/usuarios.csv")
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if usuario in df["usuario"].values:
                fila = df[df["usuario"] == usuario].iloc[0]
                if hashed == fila["password_hash"]:
                    st.session_state["usuario"] = usuario
                    st.session_state["rol"] = fila["rol"]
                    st.experimental_rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
            else:
                st.error("❌ Usuario no encontrado")
        else:
            st.error("Archivo de usuarios no encontrado.")

if "usuario" not in st.session_state:
    verificar_login()
    st.stop()

# ---------------------
# 🚀 Interfaz Principal
# ---------------------
st.sidebar.title("🔧 CMMS Fábrica")
menu_modulos = [
    "Inicio", "Máquinas", "Tareas", "Observaciones", "Inventario",
    "Servicios Externos", "Reportes", "KPIs", "Mantenimiento", "Semana"
]
seccion = st.sidebar.radio("Seleccionar módulo:", menu_modulos)

if seccion == "Inicio":
    st.title("📊 Dashboard CMMS")
    st.info(f"Bienvenido, {st.session_state['usuario'].capitalize()} 👷‍♂️")
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
# Opciones avanzadas para admin y técnico
if st.session_state.get("rol") in ["admin", "tecnico"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Opciones avanzadas")

    # Botón de backup manual
    if st.sidebar.button("📁 Backup manual a Drive"):
        with st.spinner("Realizando backup..."):
            # ✅ Personalizá esta ruta según tu PC
            carpeta_local = "C:\Users\plepratti\OneDrive - Mercopack\Escritorio\rclone"
            remoto = "cmms_drive:/CMMS_Backup/"

            comando = f"rclone copy \"{carpeta_local}\" {remoto} --progress --update"

            try:
                import subprocess
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
                if resultado.returncode == 0:
                    st.success("✅ Backup realizado con éxito.")
                else:
                    st.error(f"❌ Error en el backup:\n{resultado.stderr}")
            except Exception as e:
                st.error(f"❌ Excepción al ejecutar el backup: {e}")

# Gestión de usuarios solo para admin
if st.session_state.get("rol") == "admin":
    if st.sidebar.checkbox("🧑‍💼 Gestión de Usuarios"):
        app_usuarios(st.session_state["usuario"], st.session_state["rol"])

st.sidebar.markdown("---")
if st.sidebar.button("🔓 Cerrar sesión"):
    st.session_state.clear()
    st.experimental_rerun()
