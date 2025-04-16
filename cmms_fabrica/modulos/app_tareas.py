import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["tareas"]

def app_tareas():
    st.subheader("🛠️ Gestión de Tareas Correctivas")
    rol = st.session_state.get("rol", "invitado")

    datos = list(coleccion.find({}, {"_id": 0}))
    tareas = pd.DataFrame(datos)

    tabs = st.tabs(["📋 Ver tareas", "🛠️ Administrar tareas"])

    # --- TAB 1: VISUALIZACIÓN ---
    with tabs[0]:
        if tareas.empty:
            st.info("No hay tareas registradas.")
        else:
            filtro_estado = st.selectbox("Filtrar por estado", ["Todos"] + list(tareas["estado"].dropna().unique()))
            filtro_origen = st.selectbox("Filtrar por origen", ["Todos"] + list(tareas["origen"].dropna().unique()))

            datos = tareas.copy()
            if filtro_estado != "Todos":
                datos = datos[datos["estado"] == filtro_estado]
            if filtro_origen != "Todos":
                datos = datos[datos["origen"] == filtro_origen]

            st.dataframe(datos.sort_values("proxima_ejecucion", ascending=True), use_container_width=True)

    # --- TAB 2: CREACIÓN DE TAREAS ---
    with tabs[1]:
        if rol in ["admin", "tecnico", "produccion"]:
            st.markdown("### ➕ Agregar nueva tarea")

            nuevo_id = f"TAR{coleccion.estimated_document_count() + 1:04d}"
            with st.form(key="form_tarea"):
                st.text_input("ID de Tarea", value=nuevo_id, disabled=True)
                nueva = {}
                nueva["id_tarea"] = nuevo_id
                nueva["id_maquina"] = st.text_input("ID de Máquina")
                nueva["descripcion"] = st.text_area("Descripción")
                nueva["tipo_tarea"] = "correctiva"

                if rol == "produccion":
                    nueva["origen"] = "Producción"
                    st.info("⚠️ Esta tarea será registrada con origen *Producción*.")
                else:
                    nueva["origen"] = st.selectbox("Origen", ["manual", "observacion", "Producción"])

                nueva["ultima_ejecucion"] = st.date_input("Última ejecución").strftime("%Y-%m-%d")
                nueva["proxima_ejecucion"] = st.date_input("Próxima ejecución").strftime("%Y-%m-%d")
                nueva["estado"] = st.selectbox("Estado", ["pendiente", "cumplida"])
                nueva["observaciones"] = st.text_area("Observaciones")

                submitted = st.form_submit_button("Guardar tarea")
                if submitted:
                    coleccion.insert_one(nueva)
                    st.success("✅ Tarea agregada correctamente")
                    st.experimental_rerun()
        else:
            st.info("👁️ Solo usuarios con permisos pueden registrar nuevas tareas.")
