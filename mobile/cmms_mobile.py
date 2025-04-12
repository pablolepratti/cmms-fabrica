import streamlit as st
import pandas as pd
import datetime
import os

# Rutas a archivos CSV
DATA_FOLDER = "cmms_data"
tareas_path = os.path.join(DATA_FOLDER, "tareas.csv")
historial_path = os.path.join(DATA_FOLDER, "historial.csv")

# Cargar datos
if not os.path.exists(tareas_path):
    tareas = pd.DataFrame(columns=["ID", "ID_maquina", "Tarea", "Periodicidad", "Ultima_ejecucion"])
    tareas.to_csv(tareas_path, index=False)
else:
    tareas = pd.read_csv(tareas_path)

if not os.path.exists(historial_path):
    historial = pd.DataFrame(columns=["ID_maquina", "Tarea", "Fecha", "Usuario"])
    historial.to_csv(historial_path, index=False)
else:
    historial = pd.read_csv(historial_path)

# Interfaz mobile minimalista
st.set_page_config(page_title="CMMS Mobile", layout="centered")
st.title("📱 CMMS - Modo Móvil")

# Login básico simulado
usuario = st.text_input("Usuario")
if usuario:
    st.success(f"Bienvenido, {usuario}!")

    st.header("🧾 Tareas pendientes")
    hoy = datetime.date.today()
    tareas["Ultima_ejecucion"] = pd.to_datetime(tareas["Ultima_ejecucion"], errors="coerce")
    vencidas = tareas[tareas["Ultima_ejecucion"] < (pd.Timestamp(hoy) - pd.Timedelta(days=30))]
    st.dataframe(vencidas[["ID_maquina", "Tarea", "Periodicidad", "Ultima_ejecucion"]])

    st.header("✅ Cargar tarea realizada")
    tarea = st.selectbox("Seleccionar tarea", tareas["Tarea"].unique())
    fecha = st.date_input("Fecha", value=hoy)
    if st.button("Registrar ejecución"):
        id_maquina = tareas[tareas["Tarea"] == tarea].iloc[0]["ID_maquina"]
        tareas.loc[tareas["Tarea"] == tarea, "Ultima_ejecucion"] = fecha
        tareas.to_csv(tareas_path, index=False)

        nuevo_log = pd.DataFrame([[id_maquina, tarea, fecha, usuario]], columns=historial.columns)
        historial = pd.concat([historial, nuevo_log], ignore_index=True)
        historial.to_csv(historial_path, index=False)

        st.success(f"Tarea '{tarea}' registrada exitosamente para el {fecha}")

    st.header("🛠️ Nueva observación técnica")
    maquina = st.text_input("Máquina")
    observacion = st.text_area("Observación")
    if st.button("Guardar observación"):
        obs_path = os.path.join(DATA_FOLDER, "observaciones.csv")
        if not os.path.exists(obs_path):
            observaciones = pd.DataFrame(columns=["ID", "Máquina", "Observacion", "Fecha", "Usuario"])
        else:
            observaciones = pd.read_csv(obs_path)

        nueva = pd.DataFrame([[len(observaciones)+1, maquina, observacion, hoy, usuario]],
                             columns=["ID", "Máquina", "Observacion", "Fecha", "Usuario"])
        observaciones = pd.concat([observaciones, nueva], ignore_index=True)
        observaciones.to_csv(obs_path, index=False)
        st.success("Observación registrada")
