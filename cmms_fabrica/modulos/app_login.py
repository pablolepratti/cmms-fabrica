import streamlit as st
import hashlib
import time
from modulos.conexion_mongo import db

coleccion = db["usuarios"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cerrar_sesion():
    st.session_state.usuario = None
    st.session_state.rol = None
    st.rerun()

def login_usuario():
    st.markdown("## 🔐 Iniciar sesión en el CMMS")

    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if "rol" not in st.session_state:
        st.session_state.rol = None

    with st.form("form_login"):
        usuario = st.text_input("Usuario").strip().lower()
        password = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("Ingresar")

    if ingresar or (usuario and password and st.session_state.get("force_login", False)):
        if not usuario or not password:
            st.error("❗ Completa todos los campos.")
            return None, None

        resultado = coleccion.find_one({"usuario": usuario})

        if resultado and resultado["password_hash"] == hash_password(password):
            st.success(f"✅ Bienvenido {usuario}")
            st.session_state.usuario = usuario
            st.session_state.rol = resultado["rol"]
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
            st.session_state.force_login = False

    # Devuelve el usuario y rol desde sesión (si está logueado)
    return st.session_state.usuario, st.session_state.rol
