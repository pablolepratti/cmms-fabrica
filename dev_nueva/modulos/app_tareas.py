
import streamlit as st
from pymongo import MongoClient

def run():
    st.header("🛠️ Tareas Correctivas por Activo")

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

        st.subheader("📋 Tareas Correctivas")
        tareas = activo.get("tareas_correctivas", [])
        for i, tarea in enumerate(tareas):
            with st.expander(f"Tarea {i+1}"):
                st.json(tarea)

        st.subheader("➕ Registrar nueva tarea correctiva")
        descripcion = st.text_area("Descripción de la falla o acción correctiva")
        origen = st.selectbox("Origen", ["Observación", "Falla", "Pedido externo"])
        estado = st.selectbox("Estado", ["Pendiente", "En curso", "Finalizada"])

        if st.button("Agregar tarea"):
            if descripcion:
                nueva = {
                    "descripcion": descripcion,
                    "origen": origen,
                    "estado": estado
                }
                col.update_one({"_id": id_activo}, {"$push": {"tareas_correctivas": nueva}})
                st.success("Tarea correctiva registrada. Recargá para verla.")
            else:
                st.warning("La descripción es obligatoria.")
