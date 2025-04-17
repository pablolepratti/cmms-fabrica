import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["tareas"]

def app_tareas():
    st.subheader("🛠️ Gestión de Tareas Correctivas")
    rol = st.session_state.get("rol", "invitado")

    datos = list(coleccion.find({}, {"_id": 0}))
    for doc in datos:
        doc["id_tarea"] = str(doc["id_tarea"])
    tareas = pd.DataFrame(datos)

    tabs = st.tabs(["📋 Ver tareas", "🛠️ Administrar tareas"])

    # --- TAB 1: VISUALIZACIÓN ---
    with tabs[0]:
        if tareas.empty:
            st.info("No hay tareas registradas.")
        else:
            filtro_estado = st.selectbox("Filtrar por estado", ["Todos"] + list(tareas["estado"].dropna().unique()))
            filtro_origen = st.selectbox("Filtrar por origen", ["Todos"] + list(tareas["origen"].dropna().unique()))

            datos_filtrados = tareas.copy()
            if filtro_estado != "Todos":
                datos_filtrados = datos_filtrados[datos_filtrados["estado"] == filtro_estado]
            if filtro_origen != "Todos":
                datos_filtrados = datos_filtrados[datos_filtrados["origen"] == filtro_origen]

            st.dataframe(datos_filtrados.sort_values("proxima_ejecucion", ascending=True), use_container_width=True)

    # --- TAB 2: CREACIÓN Y ELIMINACIÓN ---
    with tabs[1]:
        if rol in ["admin", "tecnico", "produccion"]:
            st.markdown("### ➕ Agregar nueva tarea")

            nuevo_id = f"TAR{coleccion.estimated_document_count() + 1:04d}"
            with st.form(key="form_tarea"):
                st.text_input("ID de Tarea", value=nuevo_id, disabled=True)
                id_maquina = st.text_input("ID de Máquina")
                descripcion = st.text_area("Descripción")
                tipo_tarea = "correctiva"

                if rol == "produccion":
                    origen = "Producción"
                    st.info("⚠️ Esta tarea será registrada con origen *Producción*.")
                else:
                    origen = st.selectbox("Origen", ["manual", "observacion", "Producción"])

                ultima_ejecucion = st.date_input("Última ejecución").strftime("%Y-%m-%d")
                proxima_ejecucion = st.date_input("Próxima ejecución").strftime("%Y-%m-%d")
                estado = st.selectbox("Estado", ["pendiente", "cumplida"])
                observaciones = st.text_area("Observaciones")

                submitted = st.form_submit_button("Guardar tarea")

                if submitted:
                    if not id_maquina or not descripcion:
                        st.error("⚠️ Debes completar los campos 'ID de Máquina' y 'Descripción'.")
                    else:
                        nueva = {
                            "id_tarea": nuevo_id,
                            "id_maquina": id_maquina,
                            "descripcion": descripcion,
                            "tipo_tarea": tipo_tarea,
                            "origen": origen,
                            "ultima_ejecucion": ultima_ejecucion,
                            "proxima_ejecucion": proxima_ejecucion,
                            "estado": estado,
                            "observaciones": observaciones
                        }
                        coleccion.insert_one(nueva)
                        st.success("✅ Tarea agregada correctamente.")
                        st.rerun()

            st.divider()
            st.markdown("### 🗑️ Eliminar tarea existente")
            if not tareas.empty:
                id_sel = st.selectbox("Seleccionar tarea por ID", tareas["id_tarea"].tolist())
                if st.button("Eliminar tarea seleccionada"):
                    coleccion.delete_one({"id_tarea": id_sel})
                    st.success("🗑️ Tarea eliminada correctamente.")
                    st.rerun()
        else:
            st.info("👁️ Solo usuarios con permisos pueden registrar o eliminar tareas.")
