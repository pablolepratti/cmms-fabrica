import streamlit as st
import pandas as pd

def mostrar_tabla_tareas(tareas):
    if not tareas:
        st.info("No hay tareas activas.")
        return
    df = pd.DataFrame(tareas)
    df = df[["id_maquina", "descripcion", "frecuencia", "fecha_programada"]]
    df.columns = ["Máquina", "Descripción", "Frecuencia", "Fecha"]
    st.dataframe(df, use_container_width=True)

def mostrar_tabla_tareas_tecnicas(tareas_tecnicas):
    if not tareas_tecnicas:
        st.info("No hay tareas técnicas abiertas.")
        return
    df = pd.DataFrame(tareas_tecnicas)
    df = df[["titulo", "descripcion", "fecha_limite"]]
    df.columns = ["Título", "Descripción", "Fecha Límite"]
    st.dataframe(df, use_container_width=True)

def mostrar_tabla_observaciones(observaciones):
    if not observaciones:
        st.info("No hay observaciones recientes.")
        return
    df = pd.DataFrame(observaciones)
    df = df[["maquina", "descripcion", "criticidad", "fecha"]]
    df.columns = ["Máquina", "Descripción", "Criticidad", "Fecha"]
    st.dataframe(df, use_container_width=True)
