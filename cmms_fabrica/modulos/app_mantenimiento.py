import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/mantenimientos_preventivos.csv"

def cargar_mantenimientos():
    columnas = [
        "id_mantenimiento", "activo", "sector", "tipo_activo",
        "frecuencia", "modo", "tiempo_estimado", "planilla_asociada",
        "ultimo_mantenimiento", "proximo_mantenimiento", "estado", "responsable"
    ]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_mantenimientos(df):
    df.to_csv(DATA_PATH, index=False)

def app_mantenimiento():
    st.subheader("📅 Mantenimiento Preventivo Mensual")

    df = cargar_mantenimientos()
    tabs = st.tabs(["📄 Ver Plan Mensual", "🛠️ Administrar Planes"])

    # --- TAB 1: VER ---
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

    # --- TAB 2: CRUD ---
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
            if id_mantenimiento in df["id_mantenimiento"].values:
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
                df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
                guardar_mantenimientos(df)
                st.success("✅ Mantenimiento programado correctamente.")

        if len(df) > 0:
            st.markdown("### ✏️ Editar mantenimiento existente")
            id_sel = st.selectbox("Seleccionar mantenimiento por ID", df["id_mantenimiento"].tolist())
            datos = df[df["id_mantenimiento"] == id_sel].iloc[0]

            with st.form("editar_mantenimiento"):
                activo = st.text_input("Activo", value=datos["activo"])
                sector = st.text_input("Sector", value=datos["sector"])
                tipo_activo = st.text_input("Tipo de activo", value=datos["tipo_activo"])
                frecuencia = st.selectbox("Frecuencia", ["mensual", "bimensual", "trimestral", "anual"], index=["mensual", "bimensual", "trimestral", "anual"].index(datos["frecuencia"]))
                modo = st.selectbox("Modo", ["interno", "externo"], index=0 if datos["modo"] == "interno" else 1)
                tiempo_estimado = st.text_input("Tiempo estimado", value=datos["tiempo_estimado"])
                planilla_asociada = st.text_input("Planilla", value=datos["planilla_asociada"])
                ultimo_mantenimiento = st.date_input("Último mantenimiento", value=pd.to_datetime(datos["ultimo_mantenimiento"]))
                proximo_mantenimiento = st.date_input("Próximo mantenimiento", value=pd.to_datetime(datos["proximo_mantenimiento"]))
                estado = st.selectbox("Estado", ["pendiente", "realizado", "no realizado"], index=["pendiente", "realizado", "no realizado"].index(datos["estado"]))
                responsable = st.text_input("Responsable", value=datos["responsable"])
                update = st.form_submit_button("Actualizar")

            if update:
                df.loc[df["id_mantenimiento"] == id_sel, "activo"] = activo
                df.loc[df["id_mantenimiento"] == id_sel, "sector"] = sector
                df.loc[df["id_mantenimiento"] == id_sel, "tipo_activo"] = tipo_activo
                df.loc[df["id_mantenimiento"] == id_sel, "frecuencia"] = frecuencia
                df.loc[df["id_mantenimiento"] == id_sel, "modo"] = modo
                df.loc[df["id_mantenimiento"] == id_sel, "tiempo_estimado"] = tiempo_estimado
                df.loc[df["id_mantenimiento"] == id_sel, "planilla_asociada"] = planilla_asociada
                df.loc[df["id_mantenimiento"] == id_sel, "ultimo_mantenimiento"] = str(ultimo_mantenimiento)
                df.loc[df["id_mantenimiento"] == id_sel, "proximo_mantenimiento"] = str(proximo_mantenimiento)
                df.loc[df["id_mantenimiento"] == id_sel, "estado"] = estado
                df.loc[df["id_mantenimiento"] == id_sel, "responsable"] = responsable
                guardar_mantenimientos(df)
                st.success("✅ Mantenimiento actualizado correctamente.")
