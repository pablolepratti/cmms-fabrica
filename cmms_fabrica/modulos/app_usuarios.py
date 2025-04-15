import streamlit as st
import pandas as pd
import os
import hashlib

DATA_PATH = "data/usuarios.csv"

def cargar_usuarios():
    columnas = ["usuario", "password_hash", "rol"]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_usuarios(df):
    df.to_csv(DATA_PATH, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def app_usuarios(usuario_logueado, rol_logueado):
    st.subheader("👤 Gestión de Usuarios del Sistema")

    if rol_logueado != "admin":
        st.warning("Acceso restringido. Solo administradores pueden ver este módulo.")
        return

    df = cargar_usuarios()
    tabs = st.tabs(["📄 Ver Usuarios", "🛠️ Administrar Usuarios"])

    # --- TAB 1: VER ---
    with tabs[0]:
        st.dataframe(df.drop(columns=["password_hash"]), use_container_width=True)

    # --- TAB 2: CRUD ---
    with tabs[1]:
        st.markdown("### ➕ Crear nuevo usuario")
        with st.form("form_usuario"):
            nuevo_usuario = st.text_input("Nombre de usuario")
            nueva_clave = st.text_input("Contraseña", type="password")
            rol = st.selectbox("Rol", ["admin", "tecnico"])
            submitted = st.form_submit_button("Crear usuario")

        if submitted:
            if nuevo_usuario in df["usuario"].values:
                st.error("⚠️ Ya existe un usuario con ese nombre.")
            else:
                nuevo = {
                    "usuario": nuevo_usuario,
                    "password_hash": hash_password(nueva_clave),
                    "rol": rol
                }
                df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
                guardar_usuarios(df)
                st.success(f"✅ Usuario '{nuevo_usuario}' creado correctamente.")

        st.markdown("### ✏️ Cambiar contraseña de usuario existente")
        if len(df) > 0:
            usuario_sel = st.selectbox("Seleccionar usuario", df["usuario"].tolist())
            with st.form("form_pass"):
                nueva_pass = st.text_input("Nueva contraseña", type="password")
                cambiar = st.form_submit_button("Actualizar contraseña")
            if cambiar:
                df.loc[df["usuario"] == usuario_sel, "password_hash"] = hash_password(nueva_pass)
                guardar_usuarios(df)
                st.success("✅ Contraseña actualizada.")
