
import streamlit as st
from pymongo import MongoClient
from datetime import date

def run():
    st.header("👁 Observaciones Técnicas por Activo")

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

        st.subheader("📋 Observaciones registradas")
        observaciones = activo.get("observaciones", [])
        for i, obs in enumerate(observaciones):
            with st.expander(f"Observación {i+1}"):
                st.json(obs)

        st.subheader("➕ Registrar nueva observación")
        descripcion = st.text_area("Descripción de la observación")
        fecha = st.date_input("Fecha", value=date.today())
        derivada = st.checkbox("¿Derivó en tarea correctiva o técnica?")

        if st.button("Agregar observación"):
            if descripcion:
                nueva = {
                    "descripcion": descripcion,
                    "fecha": str(fecha),
                    "derivada": derivada
                }
                col.update_one({"_id": id_activo}, {"$push": {"observaciones": nueva}})
                st.success("Observación registrada. Recargá para verla.")
            else:
                st.warning("La descripción es obligatoria.")
