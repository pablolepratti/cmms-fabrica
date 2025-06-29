import streamlit as st
import pandas as pd
from cmms_fabrica.modulos.conexion_mongo import db

def cargar_coleccion(nombre):
    df = pd.DataFrame(list(db[nombre].find({}, {"_id": 0})))
    for col in df.columns:
        if "id" in col.lower():
            df[col] = df[col].astype(str)
    return df

def mostrar_kpis(compacto=False):
    df_tareas = cargar_coleccion("tareas")
    df_servicios = cargar_coleccion("servicios")
    df_mantenimiento = cargar_coleccion("mantenimientos")
    df_semana = cargar_coleccion("plan_semana")

    if compacto:
        st.markdown("### 📊 Resumen rápido")
        col1, col2, col3 = st.columns(3)
        with col1:
            pendientes = len(df_tareas[df_tareas["estado"] == "pendiente"])
            st.metric("🧰 Tareas pendientes", pendientes)
        with col2:
            vencidos = len(df_servicios[df_servicios["estado"] == "vencido"])
            st.metric("🛠️ Servicios vencidos", vencidos)
        with col3:
            no_realizados = len(df_mantenimiento[df_mantenimiento["estado"] == "no realizado"])
            st.metric("📅 Mantenimientos no realizados", no_realizados)
        return

    st.subheader("📈 Indicadores Clave de Mantenimiento")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧰 Tareas Internas")
        total = len(df_tareas)
        pendientes = len(df_tareas[df_tareas["estado"] == "pendiente"])
        realizadas = len(df_tareas[df_tareas["estado"] == "realizada"])
        cumplimiento = f"{(realizadas / total * 100):.1f}%" if total > 0 else "—"
        st.metric("Total", total)
        st.metric("Pendientes", pendientes)
        st.metric("Realizadas", realizadas)
        st.metric("Cumplimiento", cumplimiento)

    with col2:
        st.markdown("### 🛠️ Servicios Externos")
        total_s = len(df_servicios)
        vencidos = len(df_servicios[df_servicios["estado"] == "vencido"])
        realizados = len(df_servicios[df_servicios["estado"] == "realizado"])
        st.metric("Total", total_s)
        st.metric("Realizados", realizados)
        st.metric("Vencidos", vencidos)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 📅 Mantenimiento Preventivo")
        total_m = len(df_mantenimiento)
        cumplidos = len(df_mantenimiento[df_mantenimiento["estado"] == "realizado"])
        no_realizados = len(df_mantenimiento[df_mantenimiento["estado"] == "no realizado"])
        cumplimiento = f"{(cumplidos / total_m * 100):.1f}%" if total_m > 0 else "—"
        st.metric("Total planes", total_m)
        st.metric("Cumplidos", cumplidos)
        st.metric("No realizados", no_realizados)
        st.metric("Cumplimiento", cumplimiento)

    with col4:
        st.markdown("### 📆 Semana Laboral")
        total_act = len(df_semana)
        realizados = len(df_semana[df_semana["estado"] == "realizado"])
        pendientes = len(df_semana[df_semana["estado"] == "pendiente"])
        cumplimiento = f"{(realizados / total_act * 100):.1f}%" if total_act > 0 else "—"
        st.metric("Actividades totales", total_act)
        st.metric("Realizadas", realizados)
        st.metric("Pendientes", pendientes)
        st.metric("Cumplimiento", cumplimiento)

def app_kpi():
    mostrar_kpis()
