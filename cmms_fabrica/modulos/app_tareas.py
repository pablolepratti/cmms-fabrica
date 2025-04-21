import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion_mongo import db

coleccion_tareas = db["tareas"]
coleccion_maquinas = db["maquinas"]

def app_tareas():
    st.subheader("🛠️ Gestión de Tareas Correctivas")
    rol = st.session_state.get("rol", "invitado")

    datos = list(coleccion_tareas.find({}, {"_id": 0}))
    for doc in datos:
        doc["id_tarea"] = str(doc["id_tarea"])
    tareas = pd.DataFrame(datos)

    tabs = st.tabs(["📋 Ver tareas", "🛠️ Administrar tareas"])

    # TAB 1: VISUALIZACIÓN
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

            # Intentar parsear la fecha
            if "fecha_realizacion" in datos_filtrados.columns:
                datos_filtrados["fecha_realizacion"] = pd.to_datetime(datos_filtrados["fecha_realizacion"], errors='coerce')

            st.dataframe(datos_filtrados.sort_values("fecha_realizacion", ascending=True), use_container_width=True)

    # TAB 2: CREAR / EDITAR / BORRAR
    with tabs[1]:
        if rol in ["admin", "tecnico", "produccion"]:
            st.markdown("### ➕ Agregar nueva tarea")

            nuevo_id = f"TAR{coleccion_tareas.estimated_document_count() + 1:04d}"
            maquinas = [m["id_maquina"] for m in coleccion_maquinas.find({}, {"_id": 0, "id_maquina": 1})]

            with st.form(key="form_tarea"):
                st.text_input("ID de Tarea", value=nuevo_id, disabled=True)
                id_maquina = st.selectbox("ID de Máquina", maquinas)
                descripcion = st.text_area("Descripción")
                tipo_tarea = "correctiva"  # fijo

                if rol == "produccion":
                    origen = "Producción"
                    st.info("⚠️ Esta tarea será registrada con origen *Producción*.")
                else:
                    origen = st.selectbox("Origen", ["manual", "observacion", "Producción"])

                fecha_realizacion = st.date_input("Fecha de realización", value=date.today())
                estado = st.selectbox("Estado", ["pendiente", "cumplida"])
                observaciones = st.text_area("Observaciones")

                submitted = st.form_submit_button("Guardar tarea")

                if submitted:
                    if not id_maquina or not descripcion:
                        st.error("⚠️ Debes completar los campos obligatorios.")
                    else:
                        nueva = {
                            "id_tarea": nuevo_id,
                            "id_maquina": id_maquina,
                            "descripcion": descripcion,
                            "tipo_tarea": tipo_tarea,
                            "origen": origen,
                            "fecha_realizacion": str(fecha_realizacion),
                            "estado": estado,
                            "observaciones": observaciones
                        }
                        coleccion_tareas.insert_one(nueva)
                        st.success("✅ Tarea agregada correctamente.")
                        st.rerun()

            st.divider()
            st.markdown("### ✏️ Editar tarea existente")

            if not tareas.empty:
                id_sel = st.selectbox("Seleccionar tarea por ID", tareas["id_tarea"].tolist(), key="editar_id")
                datos_sel = tareas[tareas["id_tarea"] == id_sel].iloc[0]

                with st.form("form_editar_tarea"):
                    id_maquina = st.selectbox("ID de Máquina", maquinas, index=maquinas.index(datos_sel["id_maquina"]))
                    descripcion = st.text_area("Descripción", value=datos_sel["descripcion"])
                    origen = st.selectbox("Origen", ["manual", "observacion", "Producción"], index=["manual", "observacion", "Producción"].index(datos_sel["origen"]))
                    fecha_realizacion = st.date_input("Fecha de realización", value=pd.to_datetime(datos_sel["fecha_realizacion"]))
                    estado = st.selectbox("Estado", ["pendiente", "cumplida"], index=["pendiente", "cumplida"].index(datos_sel["estado"]))
                    observaciones = st.text_area("Observaciones", value=datos_sel["observaciones"])
                    actualizar = st.form_submit_button("Actualizar")

                if actualizar:
                    nuevos_datos = {
                        "id_maquina": id_maquina,
                        "descripcion": descripcion,
                        "origen": origen,
                        "fecha_realizacion": str(fecha_realizacion),
                        "estado": estado,
                        "observaciones": observaciones
                    }
                    coleccion_tareas.update_one({"id_tarea": id_sel}, {"$set": nuevos_datos})
                    st.success("✅ Tarea actualizada correctamente.")
                    st.rerun()

            st.divider()
            st.markdown("### 🗑️ Eliminar tarea existente")
            if not tareas.empty:
                id_del = st.selectbox("Seleccionar tarea por ID para eliminar", tareas["id_tarea"].tolist(), key="eliminar_id")
                if st.button("Eliminar tarea seleccionada"):
                    coleccion_tareas.delete_one({"id_tarea": id_del})
                    st.success("🗑️ Tarea eliminada correctamente.")
                    st.rerun()

        else:
            st.warning("⚠️ Solo usuarios con permisos pueden gestionar tareas.")
