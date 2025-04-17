import streamlit as st
import pandas as pd
import hashlib

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
from modulos.conexion_mongo import db

# 📱 Layout adaptativo
try:
    is_mobile = st.runtime.scriptrunner.get_script_run_context().client.display_width < 768
except:
    is_mobile = False
st.set_page_config(page_title="CMMS Fábrica", layout="centered" if is_mobile else "wide")

# 🧠 Inicializar sesión
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "rol" not in st.session_state:
    st.session_state["rol"] = None

# 🔐 Login
coleccion_usuarios = db["usuarios"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login():
    st.sidebar.subheader("🔑 Iniciar sesión")
    with st.sidebar.form("form_login"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("Ingresar")
    if ingresar:
        usuario_data = coleccion_usuarios.find_one({"usuario": usuario})
        if usuario_data and hash_password(password) == usuario_data["password_hash"]:
            st.session_state["usuario"] = usuario
            st.session_state["rol"] = usuario_data["rol"]
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")

if not st.session_state["usuario"]:
    verificar_login()
    st.stop()

# 🚀 Interfaz principal
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

# 👥 Admin: gestión de usuarios
if st.session_state["rol"] == "admin":
    if st.sidebar.checkbox("🧑‍💼 Gestión de Usuarios"):
        app_usuarios(st.session_state["usuario"], st.session_state["rol"])

# 🔓 Logout
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()
