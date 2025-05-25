
import streamlit as st
from pymongo import MongoClient

def run():
    st.header("📋 Activos Técnicos")

    # Conectar a MongoDB
    client = MongoClient("mongodb://localhost:27017")  # Cambiar si usás Mongo Atlas
    db = client["cmms"]
    coleccion = db["activos_tecnicos"]

    # Obtener todos los activos
    activos = list(coleccion.find())

    # Mostrar en tabla con opciones
    for activo in activos:
        with st.expander(f"🧱 {activo.get('nombre', 'Sin nombre')} ({activo['_id']})"):
            st.write(f"**Sector:** {activo.get('sector', 'No definido')}")
            st.write("### 🧰 Tareas Preventivas")
            st.json(activo.get("tareas_preventivas", []))
            st.write("### 🔧 Tareas Correctivas")
            st.json(activo.get("tareas_correctivas", []))
            st.write("### 🧪 Tareas Técnicas")
            st.json(activo.get("tareas_tecnicas", []))
            st.write("### 🎯 Calibraciones")
            st.json(activo.get("calibraciones", []))
            st.write("### 👁 Observaciones")
            st.json(activo.get("observaciones", []))
            st.write("### 🔄 Historial")
            st.json(activo.get("historial", []))
            st.write("### 🧴 Repuestos Usados")
            st.json(activo.get("repuestos_usados", []))
