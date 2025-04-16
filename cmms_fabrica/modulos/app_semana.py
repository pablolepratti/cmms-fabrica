import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

PLAN_PATH = "data/plan_semana.csv"
TAREAS_PATH = "data/tareas.csv"
MANTENIMIENTOS_PATH = "data/mantenimientos_preventivos.csv"

def cargar_semana():
    columnas = ["fecha", "dia", "actividad", "equipo", "estado", "notas"]
    if os.path.exists(PLAN_PATH):
        return pd.read_csv(PLAN_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_semana(df):
    df.to_csv(PLAN_PATH, index=False)

def obtener_semana_actual():
    hoy = datetime.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
    return [(inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6)], dias

def cargar_tareas_pendientes():
    if os.path.exists(TAREAS_PATH):
        df = pd.read_csv(TAREAS_PATH)
        return df[df["estado"] == "pendiente"]
    return pd.DataFrame()

def cargar_mantenimientos():
    if os.path.exists(MANTENIMIENTOS_PATH):
        return pd.read_csv(MANTENIMIENTOS_PATH)
    return pd.DataFrame()

def app_semana():
    st.subheader("📅 Planificación de Semana Laboral")

    df = cargar_semana()
    fechas, dias_semana = obtener_semana_actual()
    tareas_pendientes = cargar_tareas_pendientes()
    mantenimientos = cargar_mantenimientos()

    tabs = st.tabs(["📄 Ver Semana", "🛠️ Planificar Semana"])

    # --- TAB 1: VER SEMANA ---
    with tabs[0]:
        st.markdown("### 📆 Semana actual")
        df_semana = df[df["fecha"].isin(fechas)]
        if df_semana.empty:
            st.info("No hay actividades cargadas para esta semana.")
        else:
            df_semana = df_semana.sort_values("fecha")
            st.dataframe(df_semana, use_container_width=True)

    # --- TAB 2: PLANIFICACIÓN DE TAREAS Y MANTENIMIENTOS ---
    with tabs[1]:
        st.markdown("### 🛠️ Agendar tareas correctivas")

        if tareas_pendientes.empty:
            st.info("No hay tareas pendientes registradas.")
        else:
            tareas_pendientes = tareas_pendientes.reset_index(drop=True)
            seleccionadas_tareas = st.multiselect(
                "Seleccionar tareas a planificar",
                tareas_pendientes.index,
                format_func=lambda i: f"{tareas_pendientes.loc[i, 'id_tarea']} – {tareas_pendientes.loc[i, 'descripcion'][:40]}"
            )

            if seleccionadas_tareas:
                with st.form("form_planificar_tareas"):
                    fecha_tarea = st.selectbox("Día para asignar tareas", fechas, format_func=lambda x: f"{x} ({dias_semana[fechas.index(x)]})")
                    responsable = st.text_input("Responsable para tareas")
                    notas_tarea = st.text_area("Observaciones generales para tareas")
                    confirmar_tareas = st.form_submit_button("✅ Agendar tareas seleccionadas")

                if confirmar_tareas:
                    for i in seleccionadas_tareas:
                        tarea = tareas_pendientes.loc[i]
                        nueva = {
                            "fecha": fecha_tarea,
                            "dia": dias_semana[fechas.index(fecha_tarea)],
                            "actividad": f"[TAREA] {tarea['descripcion']}",
                            "equipo": tarea["id_maquina"],
                            "estado": "pendiente",
                            "notas": f"ID: {tarea['id_tarea']} – Responsable: {responsable} – {notas_tarea}"
                        }
                        df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)

                    guardar_semana(df)
                    st.success(f"✅ {len(seleccionadas_tareas)} tarea(s) planificadas correctamente.")

        st.markdown("---")
        st.markdown("### 🧰 Agendar mantenimientos programados")

        if mantenimientos.empty:
            st.info("No hay mantenimientos registrados.")
        else:
            mantenimientos = mantenimientos.reset_index(drop=True)
            seleccionados_mant = st.multiselect(
                "Seleccionar mantenimientos a planificar",
                mantenimientos.index,
                format_func=lambda i: f"{mantenimientos.loc[i, 'id_mantenimiento']} – {mantenimientos.loc[i, 'activo'][:40]}"
            )

            if seleccionados_mant:
                with st.form("form_planificar_mant"):
                    fecha_mant = st.selectbox("Día para asignar mantenimientos", fechas, format_func=lambda x: f"{x} ({dias_semana[fechas.index(x)]})")
                    responsable_m = st.text_input("Responsable para mantenimientos")
                    notas_mant = st.text_area("Observaciones generales para mantenimientos")
                    confirmar_mant = st.form_submit_button("✅ Agendar mantenimientos seleccionados")

                if confirmar_mant:
                    for i in seleccionados_mant:
                        mant = mantenimientos.loc[i]
                        nueva = {
                            "fecha": fecha_mant,
                            "dia": dias_semana[fechas.index(fecha_mant)],
                            "actividad": f"[MANTENIMIENTO] {mant['modo']} – {mant['tipo_activo']}",
                            "equipo": mant["activo"],
                            "estado": "pendiente",
                            "notas": f"ID: {mant['id_mantenimiento']} – Responsable: {responsable_m} – {notas_mant}"
                        }
                        df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)

                    guardar_semana(df)
                    st.success(f"✅ {len(seleccionados_mant)} mantenimiento(s) planificados correctamente.")
