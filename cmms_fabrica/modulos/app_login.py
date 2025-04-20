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

    # 👉 Detección de pantalla móvil (simple)
    is_mobile = st.session_state.get("is_mobile", False)
    if st.browser.user_agent and "Mobile" in st.browser.user_agent:
        is_mobile = True
        st.session_state.is_mobile = True

    with st.form("form_login"):
        col1, col2 = st.columns(2)
        with col1:
            usuario = st.text_input("👤 Usuario", key="login_user")
        with col2:
            password = st.text_input("🔑 Contraseña", type="password", key="login_pass")

        submit = st.form_submit_button("Ingresar")

        # ⌨️ También permite login con Enter
        if submit or (usuario and password and st.session_state.get("Enter_pressed")):
            if not usuario or not password:
                st.error("⚠️ Debes completar todos los campos.")
            else:
                usuario = usuario.strip().lower()
                user = coleccion.find_one({"usuario": usuario})
                if user and user["password_hash"] == hash_password(password):
                    st.success("✅ Bienvenido.")
                    st.session_state.usuario = user["usuario"]
                    st.session_state.rol = user["rol"]
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

def cerrar_sesion():
    st.sidebar.markdown("---")
    st.sidebar.button("🚪 Cerrar sesión", on_click=reset_sesion)

def reset_sesion():
    st.session_state.usuario = None
    st.session_state.rol = None
    st.rerun()
