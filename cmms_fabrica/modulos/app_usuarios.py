"""
📄 Módulo de Gestión de Usuarios – CMMS Fábrica

Normas aplicables: ISO 9001:2015 | ISO 27001

Descripción: Permite registrar, visualizar, modificar y eliminar usuarios con control de roles y acceso restringido.
*Solo accesible para administradores.*
"""

import streamlit as st
import pandas as pd
from cmms_fabrica.modulos.conexion_mongo import db, mongo_error
from cmms_fabrica.modulos.app_login import hash_password
from cmms_fabrica.crud.generador_historial import registrar_evento_historial


def app_usuarios(usuario_logueado: str, rol_logueado: str) -> None:
    if db is None:
        st.error(f"No hay conexión con MongoDB. {mongo_error}")
        st.stop()

    coleccion = db["usuarios"]

    st.title("👥 Gestión de Usuarios del Sistema")

    if rol_logueado != "admin":
        st.warning("⚠️ Acceso restringido. Solo administradores pueden acceder a este módulo.")
        return

    menu = ["Registrar Usuario", "Ver Usuarios", "Editar Usuario", "Eliminar Usuario"]
    accion = st.sidebar.radio("Acción", menu)

    datos = list(coleccion.find({}, {"_id": 0}))
    df = pd.DataFrame(datos)

    if accion == "Ver Usuarios":
        st.subheader("📋 Usuarios Registrados")
        if df.empty:
            st.info("No hay usuarios registrados.")
        else:
            for u in sorted(datos, key=lambda x: x.get("usuario", "")):
                st.code(f"Usuario: {u.get('usuario', '')}", language="yaml")
                st.markdown(f"- **Rol:** {u.get('rol', '')}")

    elif accion == "Registrar Usuario":
        st.subheader("➕ Crear Nuevo Usuario")
        with st.form("form_nuevo_usuario"):
            nuevo_usuario = st.text_input("Nombre de usuario").strip().lower()
            nueva_clave = st.text_input("Contraseña", type="password")
            rol = st.selectbox("Rol", ["admin", "tecnico", "produccion", "invitado"])
            submitted = st.form_submit_button("Crear Usuario")

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
                registrar_evento_historial(
                    tipo_evento="Alta usuario",
                    id_activo="-",
                    descripcion=f"Usuario creado con rol: {rol}",
                    usuario=usuario_logueado,
                    id_origen=nuevo_usuario,
                )
                st.success(f"✅ Usuario '{nuevo_usuario}' creado correctamente.")
                st.rerun()

    elif accion == "Editar Usuario":
        st.subheader("✏️ Modificar Contraseña de Usuario")
        if df.empty:
            st.info("No hay usuarios registrados.")
        else:
            usuarios_disponibles = [u for u in df["usuario"].tolist() if u != usuario_logueado]
            if not usuarios_disponibles:
                st.info("No hay otros usuarios editables.")
                return

            usuario_sel = st.selectbox("Seleccionar usuario", usuarios_disponibles)

            with st.form("form_actualizar_pass"):
                nueva_pass = st.text_input("Nueva contraseña", type="password")
                cambiar = st.form_submit_button("Actualizar Contraseña")

            if cambiar:
                if not nueva_pass:
                    st.error("⚠️ La nueva contraseña no puede estar vacía.")
                else:
                    coleccion.update_one(
                        {"usuario": usuario_sel},
                        {"$set": {"password_hash": hash_password(nueva_pass)}}
                    )
                    registrar_evento_historial(
                        tipo_evento="Modificación usuario",
                        id_activo="-",
                        descripcion="Contraseña modificada",
                        usuario=usuario_logueado,
                        id_origen=usuario_sel,
                    )
                    st.success(f"✅ Contraseña de '{usuario_sel}' actualizada correctamente.")
                    st.rerun()

    elif accion == "Eliminar Usuario":
        st.subheader("🗑️ Eliminar Usuario")
        if df.empty:
            st.info("No hay usuarios registrados.")
        else:
            usuarios_disponibles = [u for u in df["usuario"].tolist() if u != usuario_logueado]
            if not usuarios_disponibles:
                st.info("No hay otros usuarios eliminables.")
                return

            usuario_sel = st.selectbox("Seleccionar usuario", usuarios_disponibles)

            if st.button("Eliminar Usuario Seleccionado"):
                coleccion.delete_one({"usuario": usuario_sel})
                registrar_evento_historial(
                    tipo_evento="Baja usuario",
                    id_activo="-",
                    descripcion="Usuario eliminado",
                    usuario=usuario_logueado,
                    id_origen=usuario_sel,
                )
                st.success(f"🗑️ Usuario '{usuario_sel}' eliminado correctamente.")
                st.rerun()


if __name__ == "__main__":
    app_usuarios("admin", "admin")
