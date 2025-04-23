import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
from modulos.conexion_mongo import db

# Mapeo de colecciones
FUENTES = {
    "Tareas": db["tareas"],
    "Observaciones": db["observaciones"],
    "Servicios": db["servicios"],
    "Mantenimiento Preventivo": db["mantenimientos"],
    "Semana Laboral": db["plan_semana"],
    "Historial": db["historial"],
    "Calibraciones": db["calibraciones"]  # NUEVO
}

class PDF(FPDF):
    def header(self):
        try:
            self.image("logo_fabrica.png", x=10, y=8, w=30)
        except:
            pass  # Si no hay logo, que no explote
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Reporte del Sistema CMMS", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, df):
        self.set_font("Arial", "B", 9)
        for col in df.columns[:6]:
            self.cell(32, 8, str(col)[:15], border=1)
        self.ln()

        self.set_font("Arial", "", 9)
        for i, row in df.iterrows():
            for val in row[:6]:
                self.cell(32, 8, str(val)[:15], border=1)
            self.ln()

def generar_pdf(nombre_reporte, df):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.chapter_title(f"Reporte: {nombre_reporte}")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)
    pdf.chapter_body(df)

    nombre_archivo = f"reporte_{nombre_reporte.lower().replace(' ', '_')}.pdf"
    path = os.path.join("reportes", nombre_archivo)
    os.makedirs("reportes", exist_ok=True)
    pdf.output(path)
    return path

def mostrar_reportes():
    st.subheader("📄 Reportes del Sistema CMMS")

    opcion = st.selectbox("Seleccionar fuente de datos", list(FUENTES.keys()))
    coleccion = FUENTES[opcion]

    datos = list(coleccion.find({}, {"_id": 0}))
    if not datos:
        st.warning("No hay datos en esta colección.")
        return

    df = pd.DataFrame(datos)

    for col in df.columns:
        if "id" in col.lower():
            df[col] = df[col].astype(str)

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
