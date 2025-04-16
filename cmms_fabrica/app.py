import streamlit as st
import pandas as pd
import hashlib
import os
import platform

from modulos.conexion_mongo import db
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

# ---------------------
# 📱 Responsive layout
# ---------------------
try:
    is_mobile = st.runtime.scriptrunner.get_script_run_context().client.display_width < 768
except:
    is_mobile = False

layout_mode = "wide" if not is_mobile else "centered"
st.set_page_config(page_title="CMMS Fábrica", layout=layout_mode)

# ---------------------
# 🔐 Login desde MongoDB
# ---------------------
def verificar_login():
    st.sidebar.subheader("🔑 Iniciar sesión")
    with st.sidebar.form("form_login"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        ver_hash = st.checkbox("🧪 Ver hash de esta contraseña")
        ingresar = st.form_submit_button("Ingresar")

    if ver_hash:
        st.sidebar.code(hashlib.sha256(password.encode()).hexdigest(), language="bash")

    if ingresar:
        coleccion_usuarios = db["usuarios"]
        fila = coleccion_usuarios.find_one({"usuario": usuario})
        if fila:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if hashed == fila["password_hash"]:
                st.session_state["usuario"] = usuario
                st.session_state["rol"] = fila["rol"]
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
        else:
            st.error("❌ Usuario no encontrado")

if "usuario" not in st.session_state:
    verificar_login()
    st.stop()

# ---------------------
# 🚀 Interfaz Principal
# ---------------------
st.sidebar.title("🔧 CMMS Fábrica")
seccion = st.sidebar.radio("Seleccionar módulo:", [
    "Inicio", "Máquinas", "Tareas", "Observaciones", "Inventario",
    "Servicios Externos", "Reportes", "KPIs", "Mantenimiento", "Semana"
])

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

# ---------------------
# ⚙️ Opciones Avanzadas
# ---------------------
rol = st.session_state.get("rol")
es_windows = platform.system() == "Windows"

if rol in ["admin", "tecnico"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Opciones avanzadas")

    if es_windows:
        if st.sidebar.button("📁 Backup manual a Drive"):
            with st.spinner("Realizando backup..."):
                carpeta_local = r"C:\Users\plepratti\OneDrive - Mercopack\Escritorio\rclone"
                rclone_path = r"C:\Users\plepratti\OneDrive - Mercopack\Escritorio\rclone\rclone.exe"
                remoto = "cmms_drive:/CMMS_Backup/"
                comando = f'"{rclone_path}" copy "{carpeta_local}" {remoto} --progress --update'

                try:
                    import subprocess
                    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
                    if resultado.returncode == 0:
                        st.success("✅ Backup realizado con éxito.")
                    else:
                        st.error(f"❌ Error en el backup:\n{resultado.stderr}")
                except Exception as e:
                    st.error(f"❌ Excepción al ejecutar el backup: {e}")
    else:
        st.sidebar.warning("⚠️ El backup manual solo está disponible desde una PC con Windows.")

# ---------------------
# 👥 Gestión de usuarios
# ---------------------
if rol == "admin":
    if st.sidebar.checkbox("🧑‍💼 Gestión de Usuarios"):
        app_usuarios(st.session_state["usuario"], rol)

# ---------------------
# 🔓 Cierre de sesión
# ---------------------
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Cerrar sesión"):
    if rol in ["admin", "tecnico"] and es_windows:
        with st.spinner("Realizando backup antes de cerrar sesión..."):
            carpeta_local = r"C:\Users\plepratti\OneDrive - Mercopack\Escritorio\rclone"
            rclone_path = r"C:\Users\plepratti\OneDrive - Mercopack\Escritorio\rclone\rclone.exe"
            remoto = "cmms_drive:/CMMS_Backup/"
            comando = f'"{rclone_path}" copy "{carpeta_local}" {remoto} --progress --update'

            try:
                import subprocess
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
                if resultado.returncode == 0:
                    st.success("✅ Backup realizado antes de cerrar sesión.")
                else:
                    st.warning(f"⚠️ Backup con errores:\n{resultado.stderr}")
            except Exception as e:
                st.warning(f"⚠️ No se pudo hacer el backup: {e}")

    st.session_state.clear()
    st.rerun()
