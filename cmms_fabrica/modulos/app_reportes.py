import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
from modulos.conexion_mongo import db

# Mapear colecciones reales
FUENTES = {
    "Tareas": db["tareas"],
    "Observaciones": db["observaciones"],
    "Servicios": db["servicios"],
    "Mantenimiento Preventivo": db["mantenimientos"],
    "Semana Laboral": db["plan_semana"],
    "Historial": db["historial"]
}

def generar_pdf(nombre_reporte, df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Reporte: {nombre_reporte}", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    # Encabezados
    pdf.set_font("Arial", "B", 9)
    for col in df.columns[:6]:  # Limitar columnas por espacio
        pdf.cell(32, 8, str(col)[:15], border=1)
    pdf.ln()

    # Filas
    pdf.set_font("Arial", "", 9)
    for i, row in df.iterrows():
        for val in row[:6]:
            pdf.cell(32, 8, str(val)[:15], border=1)
        pdf.ln()

    nombre_archivo = f"reporte_{nombre_reporte.lower().replace(' ', '_')}.pdf"
    path = os.path.join("reportes", nombre_archivo)
    os.makedirs("reportes", exist_ok=True)
    pdf.output(path)
    return path

def mostrar_reportes():
    st.subheader("🖨️ Reportes del Sistema CMMS")

    opcion = st.selectbox("Seleccionar fuente de datos", list(FUENTES.keys()))
    coleccion = FUENTES[opcion]

    # Cargar datos desde Mongo
    datos = list(coleccion.find({}, {"_id": 0}))
    if not datos:
        st.warning("No hay datos en esta colección.")
        return

    df = pd.DataFrame(datos)
    st.dataframe(df.tail(20), use_container_width=True)

    if st.button("📄 Generar PDF de todo el reporte"):
        archivo = generar_pdf(opcion, df)
        with open(archivo, "rb") as f:
            st.download_button(
                label="⬇️ Descargar PDF",
                data=f,
                file_name=os.path.basename(archivo),
                mime="application/pdf"
            )

def app_reportes():
    mostrar_reportes()
