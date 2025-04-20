import streamlit as st
import hashlib
import time
from modulos.conexion_mongo import db

coleccion = db["usuarios"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_usuario():
    st.markdown("## 🔐 Iniciar sesión en el CMMS")

    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if "rol" not in st.session_state:
        st.session_state.rol = None

    # 👉 Detección de pantalla móvil (desactivado por compatibilidad)
    st.session_state.is_mobile = False

    with st.form("form_login"):
        usuario = st.text_input("Usuario").strip().lower()
        password = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("Ingresar")

    # Permitir login con ENTER
    if ingresar or (usuario and password):
        if not usuario or not password:
            st.error("❗ Completa todos los campos.")
            return None

        resultado = coleccion.find_one({"usuario": usuario})

        if resultado and resultado["password_hash"] == hash_password(password):
            st.success(f"✅ Bienvenido {usuario}")
            st.session_state.usuario = usuario
            st.session_state.rol = resultado["rol"]
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

    return None

def cerrar_sesion():
    st.session_state.clear()
    st.success("🔒 Sesión cerrada.")
    time.sleep(1)
    st.rerun()
