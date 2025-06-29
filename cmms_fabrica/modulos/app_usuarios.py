"""Gestión de usuarios del CMMS.

Este módulo permite registrar, visualizar, editar y eliminar usuarios del
sistema. Su implementación sigue las buenas prácticas de trazabilidad
documental establecidas en ISO 9001:2015 y considera directrices de
seguridad basadas en ISO 27001.
"""

import streamlit as st
import pandas as pd

from modulos.conexion_mongo import db
from modulos.app_login import hash_password

coleccion = db["usuarios"]


def app_usuarios(usuario_logueado: str, rol_logueado: str) -> None:
    """Interfaz principal para administrar los usuarios."""

    st.title("👥 Gestión de Usuarios del Sistema")

    if rol_logueado != "admin":
        st.warning("Acceso restringido. Solo administradores pueden ver este módulo.")
        return

    datos = list(coleccion.find({}, {"_id": 0}))
    df = pd.DataFrame(datos)

    menu = ["Registrar Usuario", "Ver Usuarios", "Editar Usuario", "Eliminar Usuario"]
    accion = st.sidebar.radio("Acción", menu)

    if accion == "Ver Usuarios":
        if df.empty:
            st.info("No hay usuarios registrados.")
        else:
            st.dataframe(df.drop(columns=["password_hash"]), use_container_width=True)

    elif accion == "Registrar Usuario":
        st.subheader("➕ Crear nuevo usuario")
        with st.form("form_nuevo_usuario"):
            nuevo_usuario = st.text_input("Nombre de usuario").strip().lower()
            nueva_clave = st.text_input("Contraseña", type="password")
            rol = st.selectbox("Rol", ["admin", "tecnico", "produccion", "invitado"])
            submitted = st.form_submit_button("Crear usuario")

        if submitted:
            if not nuevo_usuario or not nueva_clave:
                st.error("⚠️ Debes completar todos los campos.")
            elif coleccion.count_documents({"usuario": nuevo_usuario}) > 0:
                st.error("⚠️ Ya existe un usuario con ese nombre.")
            else:
                nuevo = {
                    "usuario": nuevo_usuario,
                    "password_hash": hash_password(nueva_clave),
                    "rol": rol,
                }
                coleccion.insert_one(nuevo)
                st.success(f"✅ Usuario '{nuevo_usuario}' creado correctamente.")
                st.rerun()

    elif accion == "Editar Usuario":
        st.subheader("✏️ Modificar contraseña de usuario")
        if df.empty:
            st.info("No hay usuarios registrados.")
        else:
            usuario_sel = st.selectbox(
                "Seleccionar usuario",
                [u for u in df["usuario"].tolist() if u != usuario_logueado],
            )
            with st.form("form_actualizar_pass"):
                nueva_pass = st.text_input("Nueva contraseña", type="password")
                cambiar = st.form_submit_button("Actualizar contraseña")
            if cambiar:
                if not nueva_pass:
                    st.error("⚠️ La nueva contraseña no puede estar vacía.")
                else:
                    coleccion.update_one(
                        {"usuario": usuario_sel},
                        {"$set": {"password_hash": hash_password(nueva_pass)}},
                    )
                    st.success("✅ Contraseña actualizada.")
                    st.rerun()

    elif accion == "Eliminar Usuario":
        st.subheader("🗑️ Eliminar usuario")
        if df.empty:
            st.info("No hay usuarios registrados.")
        else:
            usuario_sel = st.selectbox(
                "Seleccionar usuario",
                [u for u in df["usuario"].tolist() if u != usuario_logueado],
            )
            if st.button("Eliminar usuario seleccionado"):
                coleccion.delete_one({"usuario": usuario_sel})
                st.success(f"🗑️ Usuario '{usuario_sel}' eliminado.")
                st.rerun()
