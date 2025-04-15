import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/maquinas.csv"

def cargar_maquinas():
    columnas = [
        "id", "nombre", "tipo_activo", "sector", "estado", 
        "mantenimiento_responsable", "observaciones"
    ]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_maquinas(df):
    df.to_csv(DATA_PATH, index=False)

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
            if id_maquina in df["id"].values:
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
                df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
                guardar_maquinas(df)
                st.success("✅ Activo agregado correctamente.")

        if len(df) > 0:
            st.markdown("### ✏️ Editar activo existente")
            id_sel = st.selectbox("Seleccionar activo por ID", df["id"].tolist())
            datos = df[df["id"] == id_sel].iloc[0]

            with st.form("editar_activo"):
                nombre = st.text_input("Nombre", value=datos["nombre"])
                tipo_activo = st.text_input("Tipo de activo", value=datos["tipo_activo"])
                sector = st.text_input("Sector asignado", value=datos["sector"])
                estado = st.selectbox("Estado", ["activo", "inactivo"], index=0 if datos["estado"] == "activo" else 1)
                mantenimiento_responsable = st.selectbox("Responsable del mantenimiento", ["interno", "externo"],
                                                         index=0 if datos["mantenimiento_responsable"] == "interno" else 1)
                observaciones = st.text_area("Observaciones", value=datos["observaciones"])
                update = st.form_submit_button("Actualizar")

            if update:
                df.loc[df["id"] == id_sel, "nombre"] = nombre
                df.loc[df["id"] == id_sel, "tipo_activo"] = tipo_activo
                df.loc[df["id"] == id_sel, "sector"] = sector
                df.loc[df["id"] == id_sel, "estado"] = estado
                df.loc[df["id"] == id_sel, "mantenimiento_responsable"] = mantenimiento_responsable
                df.loc[df["id"] == id_sel, "observaciones"] = observaciones
                guardar_maquinas(df)
                st.success("✅ Activo actualizado correctamente.")
