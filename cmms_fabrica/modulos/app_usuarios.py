import streamlit as st
import pandas as pd
import hashlib
from modulos.conexion_mongo import db

coleccion = db["usuarios"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def app_usuarios(usuario_logueado, rol_logueado):
    st.subheader("👤 Gestión de Usuarios del Sistema")

    if rol_logueado != "admin":
        st.warning("Acceso restringido. Solo administradores pueden ver este módulo.")
        return

    # Cargar usuarios desde Mongo
    datos = list(coleccion.find({}, {"_id": 0}))
    df = pd.DataFrame(datos)

    tabs = st.tabs(["📄 Ver Usuarios", "🛠️ Administrar Usuarios"])

    with tabs[0]:
        if df.empty:
            st.info("No hay usuarios registrados.")
        else:
            st.dataframe(df.drop(columns=["password_hash"]), use_container_width=True)

    with tabs[1]:
        st.markdown("### ➕ Crear nuevo usuario")
        with st.form("form_usuario"):
            nuevo_usuario = st.text_input("Nombre de usuario")
            nueva_clave = st.text_input("Contraseña", type="password")
            rol = st.selectbox("Rol", ["admin", "tecnico", "produccion", "invitado"])
            submitted = st.form_submit_button("Crear usuario")

        if submitted:
            if coleccion.count_documents({"usuario": nuevo_usuario}) > 0:
                st.error("⚠️ Ya existe un usuario con ese nombre.")
            else:
                nuevo = {
                    "usuario": nuevo_usuario,
                    "password_hash": hash_password(nueva_clave),
                    "rol": rol
                }
                coleccion.insert_one(nuevo)
                st.success(f"✅ Usuario '{nuevo_usuario}' creado correctamente.")
                st.experimental_rerun()

        st.markdown("### ✏️ Cambiar contraseña de usuario existente")
        if not df.empty:
            usuario_sel = st.selectbox("Seleccionar usuario", df["usuario"].tolist())
            with st.form("form_pass"):
                nueva_pass = st.text_input("Nueva contraseña", type="password")
                cambiar = st.form_submit_button("Actualizar contraseña")
            if cambiar:
                coleccion.update_one(
                    {"usuario": usuario_sel},
                    {"$set": {"password_hash": hash_password(nueva_pass)}}
                )
                st.success("✅ Contraseña actualizada.")
