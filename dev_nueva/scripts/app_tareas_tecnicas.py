
import streamlit as st
from pymongo import MongoClient

def run():
    st.header("🧪 Tareas Técnicas por Activo")

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

        st.subheader("📋 Tareas Técnicas")
        tareas = activo.get("tareas_tecnicas", [])
        for i, tarea in enumerate(tareas):
            with st.expander(f"Tarea Técnica {i+1}"):
                st.json(tarea)

        st.subheader("➕ Registrar nueva tarea técnica")
        descripcion = st.text_area("Descripción")
        tipo = st.selectbox("Tipo de tarea técnica", [
            "Consulta técnica", "Presupuesto", "Relevamiento externo", "Rediseño", "Evaluación de proveedor", "Otro"
        ])
        estado = st.selectbox("Estado", ["Pendiente", "En curso", "Finalizada"])

        if st.button("Agregar tarea técnica"):
            if descripcion:
                nueva = {
                    "descripcion": descripcion,
                    "tipo": tipo,
                    "estado": estado
                }
                col.update_one({"_id": id_activo}, {"$push": {"tareas_tecnicas": nueva}})
                st.success("Tarea técnica registrada. Recargá para verla.")
            else:
                st.warning("La descripción es obligatoria.")
