
import streamlit as st
from pymongo import MongoClient
import pandas as pd
from io import BytesIO

def run():
    st.header("📊 Reportes por Activo Técnico")

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

        st.subheader("📈 Resumen general")
        total_preventivas = len(activo.get("tareas_preventivas", []))
        total_correctivas = len(activo.get("tareas_correctivas", []))
        total_tecnicas = len(activo.get("tareas_tecnicas", []))
        total_observaciones = len(activo.get("observaciones", []))
        total_calibraciones = len(activo.get("calibraciones", []))

        st.markdown(f"""
- 🧰 **Tareas Preventivas:** {total_preventivas}  
- 🛠️ **Tareas Correctivas:** {total_correctivas}  
- 🧪 **Tareas Técnicas:** {total_tecnicas}  
- 👁 **Observaciones:** {total_observaciones}  
- 🎯 **Calibraciones:** {total_calibraciones}
""")

        st.subheader("📤 Exportar datos")
        if st.button("Exportar todo como Excel"):
            df = pd.DataFrame([{
                "Activo": activo.get("nombre", ""),
                "ID": activo.get("_id"),
                "Preventivas": total_preventivas,
                "Correctivas": total_correctivas,
                "Técnicas": total_tecnicas,
                "Observaciones": total_observaciones,
                "Calibraciones": total_calibraciones
            }])
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="📥 Descargar reporte Excel",
                data=buffer.getvalue(),
                file_name=f"reporte_{id_activo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
