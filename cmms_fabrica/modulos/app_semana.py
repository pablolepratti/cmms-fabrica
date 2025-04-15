import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

DATA_PATH = "data/plan_semana.csv"

def cargar_semana():
    columnas = ["fecha", "dia", "actividad", "equipo", "estado", "notas"]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_semana(df):
    df.to_csv(DATA_PATH, index=False)

def obtener_semana_actual():
    hoy = datetime.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
    return [(inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6)], dias

def app_semana():
    st.subheader("📅 Planificación de Semana Laboral")

    df = cargar_semana()
    fechas, dias_semana = obtener_semana_actual()
    tabs = st.tabs(["📄 Ver Semana", "🛠️ Armar Semana"])

    # --- TAB 1: VISUALIZACIÓN DE SEMANA ACTUAL ---
    with tabs[0]:
        st.markdown("### 📆 Semana actual")
        df_semana = df[df["fecha"].isin(fechas)]
        if df_semana.empty:
            st.info("No hay actividades cargadas para esta semana.")
        else:
            df_semana = df_semana.sort_values("fecha")
            st.dataframe(df_semana, use_container_width=True)

    # --- TAB 2: CARGA MANUAL DE ACTIVIDAD POR DÍA ---
    with tabs[1]:
        st.markdown("### ➕ Planificar actividad")

        with st.form("form_semana"):
            fecha = st.selectbox("Día de la semana", fechas, format_func=lambda x: f"{x} ({dias_semana[fechas.index(x)]})")
            actividad = st.text_input("Actividad prevista")
            equipo = st.text_input("Equipo / Sistema relacionado")
            estado = st.selectbox("Estado", ["pendiente", "realizado", "no realizado", "reprogramado"])
            notas = st.text_area("Notas / Comentarios")
            submitted = st.form_submit_button("Agregar actividad")

        if submitted:
            nueva = {
                "fecha": fecha,
                "dia": dias_semana[fechas.index(fecha)],
                "actividad": actividad,
                "equipo": equipo,
                "estado": estado,
                "notas": notas
            }
            df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
            guardar_semana(df)
            st.success("✅ Actividad registrada para la semana.")
