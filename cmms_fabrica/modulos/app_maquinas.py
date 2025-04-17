import streamlit as st
import pandas as pd
from modulos.conexion_mongo import db

coleccion = db["maquinas"]

def cargar_maquinas():
    data = list(coleccion.find({}, {"_id": 0}))
    return pd.DataFrame(data)

def guardar_maquina(nueva_maquina):
    coleccion.insert_one(nueva_maquina)

def actualizar_maquina(id_maquina, nuevos_datos):
    coleccion.update_one({"id": id_maquina}, {"$set": nuevos_datos})

def app_maquinas():
    st.subheader("🏭 Gestión de Máquinas, Sistemas y Activos")

    df = cargar_maquinas()
    tabs = st.tabs(["📄 Ver Activos", "🛠️ Administrar Activos"])

    # --- TAB 1: VISUALIZACIÓN ---
    with tabs[0]:
        if df.empty:
            st.warning("No hay activos registrados.")
        else:
            tipo = st.selectbox("Filtrar por tipo de activo", ["Todos"] + sorted(df["tipo_activo"].dropna().unique()))
            sector = st.selectbox("Filtrar por sector", ["Todos"] + sorted(df["sector"].dropna().unique()))
            estado = st.selectbox("Filtrar por estado", ["Todos", "activo", "inactivo"])

            if tipo != "Todos":
                df = df[df["tipo_activo"] == tipo]
            if sector != "Todos":
                df = df[df["sector"] == sector]
            if estado != "Todos":
                df = df[df["estado"] == estado]

            st.dataframe(df.sort_values("nombre"), use_container_width=True)

    # --- TAB 2: CRUD ---
    with tabs[1]:
        st.markdown("### ➕ Agregar nuevo activo")
        with st.form("form_nuevo_activo"):
            col1, col2 = st.columns(2)
            with col1:
                id_maquina = st.text_input("ID del activo")
                nombre = st.text_input("Nombre")
                tipo_activo = st.text_input("Tipo de activo")
                sector = st.text_input("Sector asignado")
            with col2:
                estado = st.selectbox("Estado", ["activo", "inactivo"])
                mantenimiento_responsable = st.selectbox("Responsable del mantenimiento", ["interno", "externo"])
                observaciones = st.text_area("Observaciones")

            submitted = st.form_submit_button("Agregar activo")

        if submitted:
            if not id_maquina or not nombre or not tipo_activo or not sector:
                st.error("⚠️ Completá todos los campos obligatorios: ID, Nombre, Tipo y Sector.")
            elif id_maquina in df["id"].values:
                st.error("⚠️ Ya existe un activo con ese ID.")
            else:
                nuevo = {
                    "id": id_maquina,
                    "nombre": nombre,
                    "tipo_activo": tipo_activo,
                    "sector": sector,
                    "estado": estado,
                    "mantenimiento_responsable": mantenimiento_responsable,
                    "observaciones": observaciones
                }
                guardar_maquina(nuevo)
                st.success("✅ Activo agregado correctamente.")
                st.experimental_rerun()

        if len(df) > 0:
            st.divider()
            st.markdown("### ✏️ Editar activo existente")
            id_sel = st.selectbox("Seleccionar activo por ID", df["id"].tolist())
            datos = df[df["id"] == id_sel].iloc[0]

            with st.form("editar_activo"):
                nombre = st.text_input("Nombre", value=datos["nombre"])
                tipo_activo = st.text_input("Tipo de activo", value=datos["tipo_activo"])
                sector = st.text_input("Sector asignado", value=datos["sector"])
                estado = st.selectbox("Estado", ["activo", "inactivo"], index=0 if datos["estado"] == "activo" else 1)
                mantenimiento_responsable = st.selectbox(
                    "Responsable del mantenimiento", ["interno", "externo"],
                    index=0 if datos["mantenimiento_responsable"] == "interno" else 1)
                observaciones = st.text_area("Observaciones", value=datos["observaciones"])
                update = st.form_submit_button("Actualizar")

            if update:
                nuevos_datos = {
                    "nombre": nombre,
                    "tipo_activo": tipo_activo,
                    "sector": sector,
                    "estado": estado,
                    "mantenimiento_responsable": mantenimiento_responsable,
                    "observaciones": observaciones
                }
                actualizar_maquina(id_sel, nuevos_datos)
                st.success("✅ Activo actualizado correctamente.")
                st.rerun()
