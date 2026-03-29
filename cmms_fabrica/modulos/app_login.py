import streamlit as st
import hashlib
import secrets
import time
from cmms_fabrica.modulos.conexion_mongo import db, mongo_error

def hash_password(password: str) -> str:
    """Generate salted password hash in the form salt$hash."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(stored: str, provided: str) -> bool:
    """Verify a password against salt$hash structure."""
    try:
        salt, saved_hash = stored.split("$")
    except ValueError:
        # Compatibilidad con hashes antiguos sin sal
        return stored == hashlib.sha256(provided.encode()).hexdigest()
    return hashlib.sha256((salt + provided).encode()).hexdigest() == saved_hash

def cerrar_sesion():
    st.session_state.usuario = None
    st.session_state.rol = None
    st.success("Sesión cerrada correctamente.")
    time.sleep(1)

def login_usuario():
    # Verificar conexión antes de usar la colección
    if db is None:
        st.error(f"No hay conexión con MongoDB. {mongo_error}")
        st.stop()

    coleccion = db["usuarios"]

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

        if resultado and verify_password(resultado["password_hash"], password):
            st.success(f"✅ Bienvenido {usuario}")
            st.session_state.usuario = usuario
            st.session_state.rol = resultado["rol"]
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

    return None, None
