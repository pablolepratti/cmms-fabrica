import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/tareas.csv"

def cargar_tareas():
    columnas = [
        "id_tarea", "id_maquina", "descripcion", "tipo_tarea", "origen",
        "ultima_ejecucion", "proxima_ejecucion", "estado", "observaciones"
    ]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_tareas(df):
    df.to_csv(DATA_PATH, index=False)

def app_tareas():
    st.subheader("🗂️ Gestión de Tareas Correctivas")

    df = cargar_tareas()
    tabs = st.tabs(["📄 Ver Tareas", "🛠️ Administrar Tareas"])

    # --- TAB 1: VER ---
    with tabs[0]:
        if df.empty:
            st.warning("No hay tareas registradas.")
        else:
            estado = st.selectbox("Filtrar por estado", ["Todos", "pendiente", "realizada"])
            origen = st.selectbox("Filtrar por origen", ["Todos", "manual", "observacion"])

            if estado != "Todos":
                df = df[df["estado"] == estado]
            if origen != "Todos":
                df = df[df["origen"] == origen]

            st.dataframe(df.sort_values("proxima_ejecucion"), use_container_width=True)

    # --- TAB 2: CRUD ---
    with tabs[1]:
        st.markdown("### ➕ Cargar nueva tarea correctiva")
        with st.form("form_tarea"):
            col1, col2 = st.columns(2)
            with col1:
                id_tarea = st.text_input("ID de tarea")
                id_maquina = st.text_input("Máquina o sistema")
                descripcion = st.text_area("Descripción")
                tipo_tarea = st.selectbox("Tipo", ["mantenimiento", "inspección"])
            with col2:
                origen = st.selectbox("Origen", ["manual", "observacion"])
                ultima_ejecucion = st.date_input("Última ejecución")
                proxima_ejecucion = st.date_input("Próxima ejecución")
                estado = st.selectbox("Estado", ["pendiente", "realizada"])
                observaciones = st.text_area("Observaciones")

            submitted = st.form_submit_button("Agregar tarea")

        if submitted:
            if id_tarea in df["id_tarea"].values:
                st.error("⚠️ Ya existe una tarea con ese ID.")
            else:
                nueva = {
                    "id_tarea": id_tarea,
                    "id_maquina": id_maquina,
                    "descripcion": descripcion,
                    "tipo_tarea": tipo_tarea,
                    "origen": origen,
                    "ultima_ejecucion": str(ultima_ejecucion),
                    "proxima_ejecucion": str(proxima_ejecucion),
                    "estado": estado,
                    "observaciones": observaciones
                }
                df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
                guardar_tareas(df)
                st.success("✅ Tarea agregada correctamente.")

        if len(df) > 0:
            st.markdown("### ✏️ Editar tarea existente")
            id_sel = st.selectbox("Seleccionar tarea por ID", df["id_tarea"].tolist())
            datos = df[df["id_tarea"] == id_sel].iloc[0]

            with st.form("editar_tarea"):
                id_maquina = st.text_input("Máquina o sistema", value=datos["id_maquina"])
                descripcion = st.text_area("Descripción", value=datos["descripcion"])
                tipo_tarea = st.selectbox("Tipo", ["mantenimiento", "inspección"], index=["mantenimiento", "inspección"].index(datos["tipo_tarea"]))
                origen = st.selectbox("Origen", ["manual", "observacion"], index=["manual", "observacion"].index(datos["origen"]))
                ultima_ejecucion = st.date_input("Última ejecución", value=pd.to_datetime(datos["ultima_ejecucion"]))
                proxima_ejecucion = st.date_input("Próxima ejecución", value=pd.to_datetime(datos["proxima_ejecucion"]))
                estado = st.selectbox("Estado", ["pendiente", "realizada"], index=["pendiente", "realizada"].index(datos["estado"]))
                observaciones = st.text_area("Observaciones", value=datos["observaciones"])
                update = st.form_submit_button("Actualizar")

            if update:
                df.loc[df["id_tarea"] == id_sel, "id_maquina"] = id_maquina
                df.loc[df["id_tarea"] == id_sel, "descripcion"] = descripcion
                df.loc[df["id_tarea"] == id_sel, "tipo_tarea"] = tipo_tarea
                df.loc[df["id_tarea"] == id_sel, "origen"] = origen
                df.loc[df["id_tarea"] == id_sel, "ultima_ejecucion"] = str(ultima_ejecucion)
                df.loc[df["id_tarea"] == id_sel, "proxima_ejecucion"] = str(proxima_ejecucion)
                df.loc[df["id_tarea"] == id_sel, "estado"] = estado
                df.loc[df["id_tarea"] == id_sel, "observaciones"] = observaciones
                guardar_tareas(df)
                st.success("✅ Tarea actualizada correctamente.")
