
import streamlit as st
from pymongo import MongoClient

def run():
    st.header("🔧 Mantenimiento Preventivo por Activo")

    # Conexión a MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client["cmms"]
    col = db["activos_tecnicos"]

    # Selección de activo
    activos = list(col.find())
    opciones = {f"{a.get('nombre', 'Sin nombre')} ({a['_id']})": a['_id'] for a in activos}
    seleccion = st.selectbox("Seleccioná un activo técnico", list(opciones.keys()))

    if seleccion:
        id_activo = opciones[seleccion]
        activo = col.find_one({"_id": id_activo})

        st.subheader("📋 Tareas Preventivas")
        tareas = activo.get("tareas_preventivas", [])
        for i, tarea in enumerate(tareas):
            with st.expander(f"Tarea {i+1}"):
                st.json(tarea)

        # Agregar nueva tarea
        st.subheader("➕ Agregar nueva tarea preventiva")
        nueva = st.text_area("Descripción de la tarea")
        frecuencia = st.selectbox("Frecuencia", ["Diaria", Semanal", "Mensual", "Trimestral", "Anual"])
        if st.button("Agregar tarea"):
            if nueva:
                tarea_nueva = {"descripcion": nueva, "frecuencia": frecuencia}
                col.update_one({"_id": id_activo}, {"$push": {"tareas_preventivas": tarea_nueva}})
                st.success("Tarea agregada correctamente. Recargá para verla.")
            else:
                st.warning("La descripción no puede estar vacía.")
