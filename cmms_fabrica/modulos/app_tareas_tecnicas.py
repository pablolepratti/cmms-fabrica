import streamlit as st
import pandas as pd
from datetime import date, datetime
from modulos.conexion_mongo import db

coleccion_tta = db["tareas_tecnicas"]

def app_tareas_tecnicas():
    st.subheader("📂 Tareas Técnicas Abiertas")

    datos = list(coleccion_tta.find({}, {"_id": 0}))
    tareas = pd.DataFrame(datos)

    tabs = st.tabs(["📋 Ver tareas", "➕ Nueva / Editar / Eliminar"])

    # TAB 1: Ver tareas
    with tabs[0]:
        if tareas.empty:
            st.info("No hay tareas técnicas registradas.")
        else:
            st.dataframe(tareas.sort_values("ultima_actualizacion", ascending=False), use_container_width=True)
                        st.markdown("### ✅ Marcar tarea como finalizada")
            tareas_abiertas = tareas[tareas["estado"] != "Finalizada"]
            if tareas_abiertas.empty:
                st.info("Todas las tareas ya están finalizadas.")
            else:
                id_finalizar = st.selectbox(
                    "Seleccionar tarea a finalizar",
                    tareas_abiertas["id_tarea"].tolist(),
                    key="finalizar_id"
                )
                if st.button("Finalizar tarea seleccionada"):
                    coleccion_tta.update_one(
                        {"id_tarea": id_finalizar},
                        {"$set": {"estado": "Finalizada", "ultima_actualizacion": str(date.today())}}
                    )
                    st.success(f"✅ Tarea {id_finalizar} marcada como finalizada.")
                    st.rerun()
    # TAB 2: Nueva / Editar / Eliminar
    with tabs[1]:
        st.markdown("### ➕ Nueva tarea técnica")

        # Calcular nuevo ID
        ids_existentes = [
            int(t["id_tarea"][3:]) for t in coleccion_tta.find({}, {"_id": 0, "id_tarea": 1})
            if t["id_tarea"].startswith("TTA")
        ]
        proximo_id = max(ids_existentes) + 1 if ids_existentes else 1
        nuevo_id = f"TTA{proximo_id:04d}"

        with st.form("form_nueva_tta"):
            st.text_input("ID de Tarea Técnica", value=nuevo_id, disabled=True)
            descripcion = st.text_area("Descripción")
            equipo_asociado = st.text_input("Equipo asociado (o área)", placeholder="Ej: DLG_ENCOLADORA, CALIDAD, NILGRAF")
            responsable = st.text_input("Responsable", value="Pablo")
            tipo = st.selectbox("Tipo", ["Compra", "Instalación", "Medición", "Planificación", "Cotización", "Otros"])
            estado = st.selectbox("Estado", ["Abierta", "En espera", "En ejecución", "Finalizada"])
            prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            notas = st.text_area("Notas")
            submitted = st.form_submit_button("Guardar")

            if submitted:
                if not descripcion:
                    st.error("⚠️ Descripción obligatoria.")
                else:
                    nueva = {
                        "id_tarea": nuevo_id,
                        "descripcion": descripcion,
                        "equipo_asociado": equipo_asociado,
                        "responsable": responsable,
                        "estado": estado,
                        "tipo": tipo,
                        "prioridad": prioridad,
                        "fecha_inicio": str(date.today()),
                        "ultima_actualizacion": str(date.today()),
                        "notas": notas
                    }
                    coleccion_tta.insert_one(nueva)
                    st.success("✅ Tarea técnica registrada.")
                    st.rerun()

        st.divider()
        st.markdown("### ✏️ Editar tarea")

        if not tareas.empty:
            id_sel = st.selectbox("Seleccionar tarea", tareas["id_tarea"].tolist(), key="edit_id")
            datos_sel = tareas[tareas["id_tarea"] == id_sel].iloc[0]

            with st.form("form_editar_tta"):
                descripcion = st.text_area("Descripción", value=datos_sel["descripcion"])
                equipo_asociado = st.text_input("Equipo asociado", value=datos_sel.get("equipo_asociado", ""))
                responsable = st.text_input("Responsable", value=datos_sel.get("responsable", ""))

                tipos = ["Compra", "Instalación", "Medición", "Planificación", "Cotización", "Otros"]
                valor_tipo = datos_sel.get("tipo", "Otros")
                if valor_tipo not in tipos:
                    tipos.insert(0, valor_tipo)
                tipo = st.selectbox("Tipo", tipos, index=tipos.index(valor_tipo))

                estado = st.selectbox("Estado", ["Abierta", "En espera", "En ejecución", "Finalizada"],
                                      index=["Abierta", "En espera", "En ejecución", "Finalizada"].index(datos_sel["estado"]))

                prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"],
                                         index=["Alta", "Media", "Baja"].index(datos_sel["prioridad"]))

                notas = st.text_area("Notas", value=datos_sel.get("notas", ""))

                actualizar = st.form_submit_button("Actualizar")

            if actualizar:
                actualizados = {
                    "descripcion": descripcion,
                    "equipo_asociado": equipo_asociado,
                    "responsable": responsable,
                    "tipo": tipo,
                    "estado": estado,
                    "prioridad": prioridad,
                    "notas": notas,
                    "ultima_actualizacion": str(date.today())
                }
                coleccion_tta.update_one({"id_tarea": id_sel}, {"$set": actualizados})
                st.success("✅ Tarea actualizada.")
                st.rerun()

        st.divider()
        st.markdown("### 🗑️ Eliminar tarea")

        if not tareas.empty:
            id_del = st.selectbox("Seleccionar tarea a eliminar", tareas["id_tarea"].tolist(), key="delete_id")
            if st.button("Eliminar tarea"):
                coleccion_tta.delete_one({"id_tarea": id_del})
                st.success("🗑️ Tarea eliminada.")
                st.rerun()
