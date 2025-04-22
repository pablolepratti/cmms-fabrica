import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion_mongo import db

coleccion_tareas = db["tareas"]
coleccion_maquinas = db["maquinas"]

def app_tareas():
    st.subheader("🛠️ Tareas Correctivas")

    maquinas_cursor = coleccion_maquinas.find({}, {"_id": 0, "id": 1})
    maquinas = [m["id"] for m in maquinas_cursor if "id" in m]

    if not maquinas:
        st.error("⚠️ No se encontraron máquinas con campo 'id'. Revisar colección 'maquinas'.")
        return

    datos = list(coleccion_tareas.find({}, {"_id": 0}))
    tareas = pd.DataFrame(datos)

    tabs = st.tabs(["📋 Ver tareas", "➕ Nueva / Editar / Eliminar"])

    with tabs[0]:
        if tareas.empty:
            st.info("No hay tareas registradas.")
        else:
            if "tipo_tarea" in tareas.columns:
                tareas = tareas.drop(columns=["tipo_tarea"])
            st.dataframe(tareas.sort_values("proxima_ejecucion", ascending=True), use_container_width=True)

    with tabs[1]:
        st.markdown("### ➕ Nueva tarea correctiva")
        nuevo_id = f"TAR{coleccion_tareas.estimated_document_count() + 1:04d}"

        with st.form("form_nueva_tarea"):
            st.text_input("ID de Tarea", value=nuevo_id, disabled=True)
            id_maquina = st.selectbox("ID de Máquina", maquinas)
            descripcion = st.text_area("Descripción")
            origen = st.selectbox("Origen", ["manual", "observacion", "produccion"])
            proxima = st.date_input("Fecha prevista de ejecución", value=date.today())
            estado = st.selectbox("Estado", ["pendiente", "realizada"])
            observaciones = st.text_area("Observaciones")

            # Servicio externo (opcional)
            externo = st.checkbox("¿Realizado por servicio externo?")
            ejecutado_por = None
            if externo:
                st.markdown("#### 🧰 Datos del servicio externo")
                empresa = st.text_input("Empresa externa")
                tecnico = st.text_input("Técnico responsable")
                contacto = st.text_input("Contacto (teléfono o mail)")
                ejecutado_por = {
                    "tipo": "servicio_externo",
                    "empresa": empresa,
                    "tecnico": tecnico,
                    "contacto": contacto
                }

            submitted = st.form_submit_button("Guardar")

            if submitted:
                if not descripcion:
                    st.error("⚠️ Descripción obligatoria.")
                else:
                    nueva = {
                        "id_tarea": nuevo_id,
                        "id_maquina": id_maquina,
                        "descripcion": descripcion,
                        "origen": origen,
                        "estado": estado,
                        "ultima_ejecucion": str(date.today()),
                        "proxima_ejecucion": str(proxima),
                        "observaciones": observaciones
                    }
                    if ejecutado_por:
                        nueva["ejecutado_por"] = ejecutado_por

                    coleccion_tareas.insert_one(nueva)
                    st.success("✅ Tarea registrada.")
                    st.rerun()

        st.divider()
        st.markdown("### ✏️ Editar tarea")

        if not tareas.empty:
            id_sel = st.selectbox("Seleccionar tarea", tareas["id_tarea"].tolist(), key="edit_id")
            datos_sel = tareas[tareas["id_tarea"] == id_sel].iloc[0]

            with st.form("form_editar"):
                id_maquina = st.selectbox("ID de Máquina", maquinas, index=maquinas.index(datos_sel["id_maquina"]) if datos_sel["id_maquina"] in maquinas else 0)
                descripcion = st.text_area("Descripción", value=datos_sel["descripcion"])
                origen = st.selectbox("Origen", ["manual", "observacion", "produccion"], index=["manual", "observacion", "produccion"].index(datos_sel["origen"]))
                proxima = st.date_input("Fecha prevista", value=pd.to_datetime(datos_sel["proxima_ejecucion"]))
                estado = st.selectbox("Estado", ["pendiente", "realizada"], index=["pendiente", "realizada"].index(datos_sel["estado"]))
                observaciones = st.text_area("Observaciones", value=datos_sel["observaciones"])

                ejecutado_por = datos_sel.get("ejecutado_por", None)
                externo = st.checkbox("¿Realizado por servicio externo?", value=bool(ejecutado_por))
                if externo:
                    st.markdown("#### 🧰 Datos del servicio externo")
                    empresa = st.text_input("Empresa externa", value=ejecutado_por.get("empresa", "") if ejecutado_por else "")
                    tecnico = st.text_input("Técnico responsable", value=ejecutado_por.get("tecnico", "") if ejecutado_por else "")
                    contacto = st.text_input("Contacto", value=ejecutado_por.get("contacto", "") if ejecutado_por else "")
                    ejecutado_por = {
                        "tipo": "servicio_externo",
                        "empresa": empresa,
                        "tecnico": tecnico,
                        "contacto": contacto
                    }
                else:
                    ejecutado_por = None

                actualizar = st.form_submit_button("Actualizar")

            if actualizar:
                nuevos_datos = {
                    "id_maquina": id_maquina,
                    "descripcion": descripcion,
                    "origen": origen,
                    "estado": estado,
                    "proxima_ejecucion": str(proxima),
                    "observaciones": observaciones
                }
                if ejecutado_por:
                    nuevos_datos["ejecutado_por"] = ejecutado_por
                else:
                    nuevos_datos["ejecutado_por"] = None

                coleccion_tareas.update_one({"id_tarea": id_sel}, {"$set": nuevos_datos})
                st.success("✅ Tarea actualizada.")
                st.rerun()

        st.divider()
        st.markdown("### 🗑️ Eliminar tarea")

        if not tareas.empty:
            id_del = st.selectbox("Seleccionar tarea a eliminar", tareas["id_tarea"].tolist(), key="delete_id")
            if st.button("Eliminar tarea"):
                coleccion_tareas.delete_one({"id_tarea": id_del})
                st.success("🗑️ Tarea eliminada.")
                st.rerun()
