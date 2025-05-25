
import streamlit as st
from pymongo import MongoClient

def run():
    st.header("🎯 Calibraciones de Instrumentos (Calidad)")

    client = MongoClient("mongodb://localhost:27017")
    db = client["cmms"]
    col = db["activos_tecnicos"]

    # Filtrar solo instrumentos del sector 'Calidad'
    instrumentos = list(col.find({"sector": "Calidad"}))
    opciones = {f"{i.get('nombre', 'Instrumento sin nombre')} ({i['_id']})": i['_id'] for i in instrumentos}

    if not opciones:
        st.info("No hay instrumentos cargados bajo el sector 'Calidad'.")
        return

    seleccion = st.selectbox("Seleccioná un instrumento", list(opciones.keys()))

    if seleccion:
        id_activo = opciones[seleccion]
        instrumento = col.find_one({"_id": id_activo})

        st.subheader("📋 Calibraciones registradas")
        calibraciones = instrumento.get("calibraciones", [])
        for i, cal in enumerate(calibraciones):
            with st.expander(f"Calibración {i+1}"):
                st.json(cal)

        st.subheader("➕ Registrar nueva calibración")
        descripcion = st.text_area("Descripción")
        resultado = st.selectbox("Resultado", ["Aprobado", "Requiere ajuste", "Fuera de tolerancia"])
        fecha = st.date_input("Fecha de calibración")

        if st.button("Agregar calibración"):
            if descripcion:
                nueva = {
                    "descripcion": descripcion,
                    "resultado": resultado,
                    "fecha": str(fecha)
                }
                col.update_one({"_id": id_activo}, {"$push": {"calibraciones": nueva}})
                st.success("Calibración registrada. Recargá para verla.")
            else:
                st.warning("La descripción es obligatoria.")
