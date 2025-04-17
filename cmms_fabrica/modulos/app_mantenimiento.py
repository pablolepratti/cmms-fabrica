import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["mantenimientos"]

def cargar_mantenimientos():
    return pd.DataFrame(list(coleccion.find({}, {"_id": 0})))

def guardar_mantenimiento(nuevo):
    coleccion.insert_one(nuevo)

def actualizar_mantenimiento(id_mantenimiento, nuevos_datos):
    coleccion.update_one({"id_mantenimiento": id_mantenimiento}, {"$set": nuevos_datos})

def app_mantenimiento():
    st.subheader("🗕️ Mantenimiento Preventivo Mensual")
    df = cargar_mantenimientos()
    tabs = st.tabs(["📄 Ver Plan Mensual", "🛠️ Administrar Planes"])

    with tabs[0]:
        if df.empty:
            st.warning("No hay mantenimientos programados.")
        else:
            sector = st.selectbox("Filtrar por sector", ["Todos"] + sorted(df["sector"].dropna().unique()))
            estado = st.selectbox("Filtrar por estado", ["Todos", "pendiente", "realizado", "no realizado"])
            frecuencia = st.selectbox("Filtrar por frecuencia", ["Todas"] + sorted(df["frecuencia"].dropna().unique()))

            if sector != "Todos":
                df = df[df["sector"] == sector]
            if estado != "Todos":
                df = df[df["estado"] == estado]
            if frecuencia != "Todas":
                df = df[df["frecuencia"] == frecuencia]

            st.dataframe(df.sort_values("proximo_mantenimiento"), use_container_width=True)

    with tabs[1]:
        st.markdown("### ➕ Programar nuevo mantenimiento")
        with st.form("form_mantenimiento"):
            col1, col2 = st.columns(2)
            with col1:
                id_mantenimiento = st.text_input("ID del mantenimiento")
                activo = st.text_input("Activo")
                sector = st.text_input("Sector")
                tipo_activo = st.text_input("Tipo de activo")
                frecuencia = st.selectbox("Frecuencia", ["mensual", "bimensual", "trimestral", "anual"])
                modo = st.selectbox("Modo de ejecución", ["interno", "externo"])
            with col2:
                tiempo_estimado = st.text_input("Tiempo estimado (minutos)")
                planilla_asociada = st.text_input("Planilla asociada (PDF)")
                ultimo_mantenimiento = st.date_input("Último mantenimiento")
                proximo_mantenimiento = st.date_input("Próximo mantenimiento")
                estado = st.selectbox("Estado", ["pendiente", "realizado", "no realizado"])
                responsable = st.text_input("Responsable asignado")

            submitted = st.form_submit_button("Agregar mantenimiento")

        if submitted:
            if not id_mantenimiento or not activo or not sector:
                st.error("⚠️ Completá los campos obligatorios: ID, Activo y Sector.")
            elif id_mantenimiento in df["id_mantenimiento"].values:
                st.error("⚠️ Ya existe un mantenimiento con ese ID.")
            else:
                nuevo = {
                    "id_mantenimiento": id_mantenimiento,
                    "activo": activo,
                    "sector": sector,
                    "tipo_activo": tipo_activo,
                    "frecuencia": frecuencia,
                    "modo": modo,
                    "tiempo_estimado": tiempo_estimado,
                    "planilla_asociada": planilla_asociada,
                    "ultimo_mantenimiento": str(ultimo_mantenimiento),
                    "proximo_mantenimiento": str(proximo_mantenimiento),
                    "estado": estado,
                    "responsable": responsable
                }
                guardar_mantenimiento(nuevo)
                st.success("✅ Mantenimiento programado correctamente.")
                st.experimental_rerun()

        if len(df) > 0:
            st.divider()
            st.markdown("### ✏️ Editar mantenimiento existente")
            id_sel = st.selectbox("Seleccionar mantenimiento por ID", df["id_mantenimiento"].tolist())
            datos = df[df["id_mantenimiento"] == id_sel].iloc[0]

            with st.form("editar_mantenimiento"):
                activo = st.text_input("Activo", value=datos["activo"])
                sector = st.text_input("Sector", value=datos["sector"])
                tipo_activo = st.text_input("Tipo de activo", value=datos["tipo_activo"])
                frecuencia = st.selectbox("Frecuencia", ["mensual", "bimensual", "trimestral", "anual"],
                                          index=["mensual", "bimensual", "trimestral", "anual"].index(datos["frecuencia"]))
                modo = st.selectbox("Modo", ["interno", "externo"], index=0 if datos["modo"] == "interno" else 1)
                tiempo_estimado = st.text_input("Tiempo estimado", value=datos["tiempo_estimado"])
                planilla_asociada = st.text_input("Planilla", value=datos["planilla_asociada"])
                ultimo_mantenimiento = st.date_input("Último mantenimiento", value=pd.to_datetime(datos["ultimo_mantenimiento"]))
                proximo_mantenimiento = st.date_input("Próximo mantenimiento", value=pd.to_datetime(datos["proximo_mantenimiento"]))
                estado = st.selectbox("Estado", ["pendiente", "realizado", "no realizado"],
                                      index=["pendiente", "realizado", "no realizado"].index(datos["estado"]))
                responsable = st.text_input("Responsable", value=datos["responsable"])
                update = st.form_submit_button("Actualizar")

            if update:
                nuevos_datos = {
                    "activo": activo,
                    "sector": sector,
                    "tipo_activo": tipo_activo,
                    "frecuencia": frecuencia,
                    "modo": modo,
                    "tiempo_estimado": tiempo_estimado,
                    "planilla_asociada": planilla_asociada,
                    "ultimo_mantenimiento": str(ultimo_mantenimiento),
                    "proximo_mantenimiento": str(proximo_mantenimiento),
                    "estado": estado,
                    "responsable": responsable
                }
                actualizar_mantenimiento(id_sel, nuevos_datos)
                st.success("✅ Mantenimiento actualizado correctamente.")
                st.experimental_rerun()
