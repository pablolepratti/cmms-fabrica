import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/observaciones.csv"

def cargar_observaciones():
    columnas = [
        "id_obs", "id_maquina", "fecha", "descripcion", "autor",
        "criticidad", "crear_tarea", "estado", "tarea_relacionada"
    ]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_observaciones(df):
    df.to_csv(DATA_PATH, index=False)

def app_observaciones():
    st.subheader("📝 Observaciones Técnicas")

    df = cargar_observaciones()
    tabs = st.tabs(["📄 Ver Observaciones", "🛠️ Administrar Observaciones"])

    # --- TAB 1: VISUALIZACIÓN ---
    with tabs[0]:
        if df.empty:
            st.warning("No hay observaciones registradas.")
        else:
            crit = st.selectbox("Filtrar por criticidad", ["Todas", "baja", "media", "alta"])
            estado = st.selectbox("Filtrar por estado", ["Todas", "pendiente", "resuelta", "descartada"])

            if crit != "Todas":
                df = df[df["criticidad"] == crit]
            if estado != "Todas":
                df = df[df["estado"] == estado]

            st.dataframe(df.sort_values("fecha", ascending=False), use_container_width=True)

    # --- TAB 2: CRUD ---
    with tabs[1]:
        st.markdown("### ➕ Agregar nueva observación")
        with st.form("form_nueva_obs"):
            col1, col2 = st.columns(2)
            with col1:
                id_obs = st.text_input("ID de observación")
                id_maquina = st.text_input("Máquina o sistema")
                descripcion = st.text_area("Descripción")
                criticidad = st.selectbox("Criticidad", ["baja", "media", "alta"])
            with col2:
                estado = st.selectbox("Estado actual", ["pendiente", "resuelta", "descartada"])
                crear_tarea = st.selectbox("¿Convertir en tarea correctiva?", ["no", "sí"])
                tarea_relacionada = st.text_input("ID de tarea relacionada (opcional)")
                autor = st.text_input("Autor")

            submitted = st.form_submit_button("Agregar observación")

        if submitted:
            if id_obs in df["id_obs"].values:
                st.error("⚠️ Ya existe una observación con ese ID.")
            else:
                nueva_obs = {
                    "id_obs": id_obs,
                    "id_maquina": id_maquina,
                    "fecha": datetime.today().strftime("%Y-%m-%d"),
                    "descripcion": descripcion,
                    "autor": autor,
                    "criticidad": criticidad,
                    "crear_tarea": crear_tarea,
                    "estado": estado,
                    "tarea_relacionada": tarea_relacionada
                }
                df = pd.concat([df, pd.DataFrame([nueva_obs])], ignore_index=True)
                guardar_observaciones(df)
                st.success("✅ Observación agregada correctamente.")

        if len(df) > 0:
            st.markdown("### ✏️ Editar observación existente")
            id_sel = st.selectbox("Seleccionar observación por ID", df["id_obs"].tolist())
            datos = df[df["id_obs"] == id_sel].iloc[0]

            with st.form("editar_obs"):
                id_maquina = st.text_input("Máquina o sistema", value=datos["id_maquina"])
                descripcion = st.text_area("Descripción", value=datos["descripcion"])
                criticidad = st.selectbox("Criticidad", ["baja", "media", "alta"], index=["baja","media","alta"].index(datos["criticidad"]))
                estado = st.selectbox("Estado", ["pendiente", "resuelta", "descartada"], index=["pendiente","resuelta","descartada"].index(datos["estado"]))
                crear_tarea = st.selectbox("¿Convertir en tarea?", ["no", "sí"], index=0 if datos["crear_tarea"] == "no" else 1)
                tarea_relacionada = st.text_input("Tarea relacionada", value=datos["tarea_relacionada"])
                autor = st.text_input("Autor", value=datos["autor"])
                update = st.form_submit_button("Actualizar")

            if update:
                df.loc[df["id_obs"] == id_sel, "id_maquina"] = id_maquina
                df.loc[df["id_obs"] == id_sel, "descripcion"] = descripcion
                df.loc[df["id_obs"] == id_sel, "criticidad"] = criticidad
                df.loc[df["id_obs"] == id_sel, "estado"] = estado
                df.loc[df["id_obs"] == id_sel, "crear_tarea"] = crear_tarea
                df.loc[df["id_obs"] == id_sel, "tarea_relacionada"] = tarea_relacionada
                df.loc[df["id_obs"] == id_sel, "autor"] = autor
                guardar_observaciones(df)
                st.success("✅ Observación actualizada correctamente.")
