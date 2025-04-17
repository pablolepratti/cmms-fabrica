import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["servicios"]

def app_servicios_ext():
    st.subheader("🔧 Servicios Tercerizados")

    datos = list(coleccion.find({}, {"_id": 0}))
    df = pd.DataFrame(datos)
    tabs = st.tabs(["📄 Ver Servicios", "🛠️ Administrar Servicios"])

    # --- TAB 1: VER ---
    with tabs[0]:
        if df.empty:
            st.warning("No hay servicios registrados.")
        else:
            estado = st.selectbox("Filtrar por estado", ["Todos", "pendiente", "realizado", "vencido"])
            empresa = st.selectbox("Filtrar por empresa", ["Todas"] + sorted(df["empresa"].dropna().unique()))

            if estado != "Todos":
                df = df[df["estado"] == estado]
            if empresa != "Todas":
                df = df[df["empresa"] == empresa]

            st.dataframe(df.sort_values("proxima_fecha"), use_container_width=True)

    # --- TAB 2: CRUD ---
    with tabs[1]:
        st.markdown("### ➕ Agregar nuevo servicio")
        with st.form("form_servicio"):
            col1, col2 = st.columns(2)
            with col1:
                id_servicio = st.text_input("ID del servicio")
                id_activo = st.text_input("Activo")
                empresa = st.text_input("Empresa")
                fecha_realizacion = st.date_input("Fecha de realización")
                descripcion = st.text_area("Descripción del servicio")
            with col2:
                periodicidad = st.selectbox("Periodicidad", ["mensual", "bimensual", "trimestral", "anual"])
                proxima_fecha = st.date_input("Próxima fecha programada")
                estado = st.selectbox("Estado", ["pendiente", "realizado", "vencido"])
                responsable_fabrica = st.text_input("Responsable en fábrica")
                observaciones = st.text_area("Observaciones adicionales")

            submitted = st.form_submit_button("Agregar servicio")

        if submitted:
            if not id_servicio or not empresa or not id_activo:
                st.error("⚠️ Completá todos los campos obligatorios: ID del servicio, Empresa y Activo.")
            elif coleccion.count_documents({"id_servicio": id_servicio}) > 0:
                st.error("⚠️ Ya existe un servicio con ese ID.")
            else:
                nuevo = {
                    "id_servicio": id_servicio,
                    "id_activo": id_activo,
                    "empresa": empresa,
                    "fecha_realizacion": fecha_realizacion.strftime("%Y-%m-%d"),
                    "descripcion": descripcion,
                    "periodicidad": periodicidad,
                    "proxima_fecha": proxima_fecha.strftime("%Y-%m-%d"),
                    "estado": estado,
                    "responsable_fabrica": responsable_fabrica,
                    "observaciones": observaciones
                }
                coleccion.insert_one(nuevo)
                st.success("✅ Servicio agregado correctamente.")
                st.experimental_rerun()

        if not df.empty:
            st.divider()
            st.markdown("### ✏️ Editar servicio existente")
            id_sel = st.selectbox("Seleccionar servicio por ID", df["id_servicio"].tolist())
            datos = df[df["id_servicio"] == id_sel].iloc[0]

            with st.form("editar_servicio"):
                id_activo = st.text_input("Activo", value=datos["id_activo"])
                empresa = st.text_input("Empresa", value=datos["empresa"])
                fecha_realizacion = st.date_input("Fecha de realización", value=pd.to_datetime(datos["fecha_realizacion"]))
                descripcion = st.text_area("Descripción del servicio", value=datos["descripcion"])
                periodicidad = st.selectbox("Periodicidad", ["mensual", "bimensual", "trimestral", "anual"],
                                            index=["mensual", "bimensual", "trimestral", "anual"].index(datos["periodicidad"]))
                proxima_fecha = st.date_input("Próxima fecha", value=pd.to_datetime(datos["proxima_fecha"]))
                estado = st.selectbox("Estado", ["pendiente", "realizado", "vencido"],
                                      index=["pendiente", "realizado", "vencido"].index(datos["estado"]))
                responsable_fabrica = st.text_input("Responsable en fábrica", value=datos["responsable_fabrica"])
                observaciones = st.text_area("Observaciones", value=datos["observaciones"])
                update = st.form_submit_button("Actualizar")

            if update:
                coleccion.update_one(
                    {"id_servicio": id_sel},
                    {"$set": {
                        "id_activo": id_activo,
                        "empresa": empresa,
                        "fecha_realizacion": fecha_realizacion.strftime("%Y-%m-%d"),
                        "descripcion": descripcion,
                        "periodicidad": periodicidad,
                        "proxima_fecha": proxima_fecha.strftime("%Y-%m-%d"),
                        "estado": estado,
                        "responsable_fabrica": responsable_fabrica,
                        "observaciones": observaciones
                    }}
                )
                st.success("✅ Servicio actualizado correctamente.")
                st.rerun()
