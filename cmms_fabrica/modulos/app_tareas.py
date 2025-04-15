import streamlit as st
import pandas as pd
import os

RUTA = "data/tareas.csv"

# Cargar tareas desde CSV
def cargar_tareas():
    if os.path.exists(RUTA):
        return pd.read_csv(RUTA)
    else:
        return pd.DataFrame(columns=["id_tarea", "id_maquina", "descripcion", "tipo_tarea", "origen", "ultima_ejecucion", "proxima_ejecucion", "estado", "observaciones"])

# Guardar tareas en CSV
def guardar_tareas(df):
    df.to_csv(RUTA, index=False)

# Mostrar panel de visualización y gestión de tareas
def app_tareas():
    st.subheader("🛠️ Gestión de Tareas Correctivas")
    tareas = cargar_tareas()

    tabs = st.tabs(["📋 Ver tareas", "🛠️ Administrar tareas"])

    with tabs[0]:
        filtro_estado = st.selectbox("Filtrar por estado", ["Todos"] + list(tareas["estado"].dropna().unique()))
        filtro_origen = st.selectbox("Filtrar por origen", ["Todos"] + list(tareas["origen"].dropna().unique()))

        datos = tareas.copy()
        if filtro_estado != "Todos":
            datos = datos[datos["estado"] == filtro_estado]
        if filtro_origen != "Todos":
            datos = datos[datos["origen"] == filtro_origen]

        st.dataframe(datos, use_container_width=True)

    with tabs[1]:
        st.markdown("### ➕ Agregar nueva tarea")
        with st.form(key="form_tarea"):
            nueva = {}
            nueva["id_tarea"] = st.text_input("ID de Tarea")
            nueva["id_maquina"] = st.text_input("ID de Máquina")
            nueva["descripcion"] = st.text_area("Descripción")
            nueva["tipo_tarea"] = st.selectbox("Tipo", ["mantenimiento", "inspección"])
            nueva["origen"] = st.selectbox("Origen", ["manual", "observacion"])
            nueva["ultima_ejecucion"] = st.date_input("Última ejecución").strftime("%Y-%m-%d")
            nueva["proxima_ejecucion"] = st.date_input("Próxima ejecución").strftime("%Y-%m-%d")
            nueva["estado"] = st.selectbox("Estado", ["pendiente", "cumplida"])
            nueva["observaciones"] = st.text_area("Observaciones")
            submitted = st.form_submit_button("Guardar tarea")

            if submitted:
                tareas = tareas.append(nueva, ignore_index=True)
                guardar_tareas(tareas)
                st.success("✅ Tarea agregada correctamente")
                st.experimental_rerun()
