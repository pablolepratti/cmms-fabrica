import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["mantenimientos"]

def cargar_mantenimientos():
    df = pd.DataFrame(list(coleccion.find({}, {"_id": 0})))
    if not df.empty:
        for col in df.columns:
            if "id" in col.lower():
                df[col] = df[col].astype(str)
    return df

def guardar_mantenimiento(nuevo):
    coleccion.insert_one(nuevo)

def actualizar_mantenimiento(id_mantenimiento, nuevos_datos):
    coleccion.update_one({"id_mantenimiento": id_mantenimiento}, {"$set": nuevos_datos})

def eliminar_mantenimiento(id_mantenimiento):
    coleccion.delete_one({"id_mantenimiento": id_mantenimiento})

def app_mantenimiento():
    st.subheader("🗓️ Mantenimiento Preventivo Mensual")

    df = cargar_mantenimientos()
    tabs = st.tabs(["📄 Ver Plan Mensual", "🛠️ Administrar Planes"])

    # === TAB 1 ===
    with tabs[0]:
        if df.empty:
            st.info("No hay mantenimientos programados.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                sector = st.selectbox("Filtrar por sector", ["Todos"] + sorted(df["sector"].dropna().unique()))
            with col2:
                estado = st.selectbox("Filtrar por estado", ["Todos", "pendiente", "realizado", "no realizado"])
            with col3:
                frecuencia = st.selectbox("Filtrar por frecuencia", ["Todas"] + sorted(df["frecuencia"].dropna().unique()))

            filtrado = df.copy()
            if sector != "Todos":
                filtrado = filtrado[filtrado["sector"] == sector]
            if estado != "Todos":
                filtrado = filtrado[filtrado["estado"] == estado]
            if frecuencia != "Todas":
                filtrado = filtrado[filtrado["frecuencia"] == frecuencia]

            st.dataframe(filtrado.sort_values("proximo_mantenimiento"), use_container_width=True)

    # === TAB 2 ===
    with tabs[1]:
        st.markdown("### ➕ Programar nuevo mantenimiento")
        with st.form("form_nuevo_mantenimiento"):
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
                planilla_asociada = st.text_input("Planilla asociada (Excel)")
                ultimo_mantenimiento = st.date_input("Último mantenimiento")
                proximo_mantenimiento = st.date_input("Próximo mantenimiento")
                estado = st.selectbox("Estado", ["pendiente", "realizado", "no realizado"])
                responsable = st.text_input("Responsable asignado")

            submit_nuevo = st.form_submit_button("Agregar mantenimiento")

        if submit_nuevo:
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
                st.rerun()

        if not df.empty:
            st.divider()
            st.markdown("### ✏️ Editar mantenimiento existente")

            id_sel = st.selectbox("Seleccionar mantenimiento por ID", df["id_mantenimiento"].tolist())
            datos = df[df["id_mantenimiento"] == id_sel].iloc[0]

            with st.form("form_editar_mantenimiento"):
                col1, col2 = st.columns(2)
                with col1:
                    activo = st.text_input("Activo", value=datos.get("activo", ""))
                    sector = st.text_input("Sector", value=datos.get("sector", ""))
                    tipo_activo = st.text_input("Tipo de activo", value=datos.get("tipo_activo", ""))
                    frecuencia = st.selectbox("Frecuencia", ["mensual", "bimensual", "trimestral", "anual"],
                                              index=["mensual", "bimensual", "trimestral", "anual"].index(datos.get("frecuencia", "mensual")))
                    modo = st.selectbox("Modo", ["interno", "externo"],
                                        index=0 if datos.get("modo", "interno") == "interno" else 1)
                with col2:
                    tiempo_estimado = st.text_input("Tiempo estimado", value=datos.get("tiempo_estimado", ""))
                    planilla_asociada = st.text_input("Planilla", value=datos.get("planilla_asociada", ""))
                    ultimo_mantenimiento = st.date_input("Último mantenimiento",
                                                         value=pd.to_datetime(datos.get("ultimo_mantenimiento", datetime.now())))
                    proximo_mantenimiento = st.date_input("Próximo mantenimiento",
                                                          value=pd.to_datetime(datos.get("proximo_mantenimiento", datetime.now())))
                    estado = st.selectbox("Estado", ["pendiente", "realizado", "no realizado"],
                                          index=["pendiente", "realizado", "no realizado"].index(datos.get("estado", "pendiente")))
                    responsable = st.text_input("Responsable", value=datos.get("responsable", ""))

                submit_edit = st.form_submit_button("Actualizar mantenimiento")

            if submit_edit:
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
                st.rerun()

            st.divider()
            st.markdown("### 🗑️ Eliminar mantenimiento")
            id_del = st.selectbox("Seleccionar ID a eliminar", df["id_mantenimiento"].tolist())
            if st.button("Eliminar mantenimiento seleccionado"):
                eliminar_mantenimiento(id_del)
                st.success("🗑️ Mantenimiento eliminado correctamente.")
                st.rerun()
