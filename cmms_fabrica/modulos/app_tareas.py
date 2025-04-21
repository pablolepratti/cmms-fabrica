import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion_mongo import db

coleccion = db["tareas"]
maquinas = db["maquinas"]

def app_tareas():
    st.subheader("🛠️ Gestión de Tareas Correctivas")
    rol = st.session_state.get("rol", "invitado")

    datos = list(coleccion.find({}, {"_id": 0}))
    for doc in datos:
        doc["id_tarea"] = str(doc["id_tarea"])
    tareas = pd.DataFrame(datos)

    lista_maquinas = [m.get("id_maquina") for m in maquinas.find({}, {"_id": 0, "id_maquina": 1})]

    tabs = st.tabs(["📋 Ver tareas", "🛠️ Administrar tareas"])

    # --- TAB 1: VER ---
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

            st.dataframe(datos_filtrados.sort_values("fecha_realizacion", ascending=True), use_container_width=True)

    # --- TAB 2: CREAR / EDITAR / ELIMINAR ---
    with tabs[1]:
        if rol in ["admin", "tecnico", "produccion"]:
            st.markdown("### ➕ Agregar o modificar tarea")

            nuevo_id = f"TAR{coleccion.estimated_document_count() + 1:04d}"
            tarea_sel = st.selectbox("Seleccionar tarea existente para editar (o dejar vacío)", [""] + tareas["id_tarea"].tolist())

            datos_editar = tareas[tareas["id_tarea"] == tarea_sel].to_dict("records")[0] if tarea_sel else {}

            with st.form("form_tarea"):
                id_tarea = st.text_input("ID de Tarea", value=tarea_sel or nuevo_id, disabled=True)
                id_maquina = st.selectbox("ID de Máquina", options=lista_maquinas, index=lista_maquinas.index(datos_editar["id_maquina"]) if datos_editar else 0)
                descripcion = st.text_area("Descripción", value=datos_editar.get("descripcion", ""))
                origen = st.selectbox("Origen", ["manual", "observacion", "Producción"], index=["manual", "observacion", "Producción"].index(datos_editar.get("origen", "manual")))
                fecha_realizacion = st.date_input("Fecha de realización", value=pd.to_datetime(datos_editar.get("fecha_realizacion", date.today())))
                estado = st.selectbox("Estado", ["pendiente", "cumplida"], index=["pendiente", "cumplida"].index(datos_editar.get("estado", "pendiente")))
                observaciones = st.text_area("Observaciones", value=datos_editar.get("observaciones", ""))

                submitted = st.form_submit_button("Guardar tarea")

                if submitted:
                    if not id_maquina or not descripcion:
                        st.error("⚠️ Debes completar ID de máquina y descripción.")
                    else:
                        registro = {
                            "id_tarea": id_tarea,
                            "id_maquina": id_maquina,
                            "descripcion": descripcion,
                            "origen": origen,
                            "fecha_realizacion": fecha_realizacion.strftime("%Y-%m-%d"),
                            "estado": estado,
                            "observaciones": observaciones
                        }

                        if tarea_sel:
                            coleccion.update_one({"id_tarea": id_tarea}, {"$set": registro})
                            st.success("✅ Tarea actualizada.")
                        else:
                            coleccion.insert_one(registro)
                            st.success("✅ Tarea agregada.")
                        st.rerun()

            st.divider()
            st.markdown("### 🗑️ Eliminar tarea")
            if not tareas.empty:
                id_del = st.selectbox("Seleccionar tarea por ID para eliminar", tareas["id_tarea"].tolist())
                if st.button("Eliminar tarea seleccionada"):
                    coleccion.delete_one({"id_tarea": id_del})
                    st.success("🗑️ Tarea eliminada.")
                    st.rerun()
        else:
            st.info("👁️ Solo usuarios con permisos pueden registrar o eliminar tareas.")
