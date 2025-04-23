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
    st.success("Sesión cerrada correctamente.")
    time.sleep(1)

def login_usuario():
    # Si ya hay un usuario logueado, no mostrar el login
    if st.session_state.get("usuario") and st.session_state.get("rol"):
        return st.session_state.usuario, st.session_state.rol

    st.markdown("## 🔐 Iniciar sesión en el CMMS")

    with st.form("form_login"):
        usuario = st.text_input("Usuario").strip().lower()
        password = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("Ingresar")

    if ingresar:
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

    return None, None
